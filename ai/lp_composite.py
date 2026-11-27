"""Sustitución de la cabeza de la presentadora por la presentadora virtual animada (salida de lp_reenact.py).
- Quita la cabeza original usando el fondo de estudio exacto y la alfa RVM de la presentadora.
- Coloca la cabeza nueva (recorte 512 de LivePortrait) con su propia alfa (RVM sobre los recortes generados).
- Funde el cuello con el cuerpo original en una franja bajo el mentón e iguala el tono de piel del cuello.
- Subtítulos, cuerpo, manos y fondo no se tocan. Audio: el del máster (original).
Uso: lp_composite.py <config.json>
config: master, t0, t1, src_offset (seg. del original que corresponden al 0 del máster), lp_dir, gen_alpha_dir,
        alpha_dir (alfa presentadora, índice ordinal del original), bg, bgRanges, out"""
import sys, os, json, subprocess
import numpy as np, cv2, av

cfg = json.load(open(sys.argv[1])); meta = json.load(open(os.path.join(cfg["lp_dir"], "meta.json")))
fps = meta["fps"]; W, H = 1920, 1080
bg0 = np.load(cfg["bg"]).astype(np.float32)
bgr = [(a, b, np.load(p).astype(np.float32)) for a, b, p in cfg.get("bgRanges", [])]
info = {f["i"]: f for f in meta["frames"]}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(5)

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def skin_mask(rgb):
    """Probabilidad de piel (YCrCb), suave. rgb float 0-1."""
    ycc = cv2.cvtColor((np.clip(rgb, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2YCrCb).astype(np.float32)
    cr, cb, y = ycc[..., 1], ycc[..., 2], ycc[..., 0]
    m = smoothstep(128, 138, cr) * (1 - smoothstep(172, 182, cr)) * smoothstep(75, 85, cb) * (1 - smoothstep(128, 138, cb)) * smoothstep(40, 70, y)
    return cv2.GaussianBlur(m, (0, 0), 2)

def lab(rgb): return cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2Lab)
def rgb_from_lab(x): return np.clip(cv2.cvtColor(x.astype(np.float32), cv2.COLOR_Lab2RGB), 0, 1)

def pyr_blend(a, b, m, levels=5):
    """Mezcla multibanda (pirámide laplaciana): a donde m=0, b donde m=1."""
    ga, gb, gm = [a], [b], [m]
    for _ in range(levels):
        ga.append(cv2.pyrDown(ga[-1])); gb.append(cv2.pyrDown(gb[-1])); gm.append(cv2.pyrDown(gm[-1]))
    out = ga[-1] * (1 - gm[-1][..., None]) + gb[-1] * gm[-1][..., None]
    for l in range(levels - 1, -1, -1):
        sz = (ga[l].shape[1], ga[l].shape[0])
        la = ga[l] - cv2.pyrUp(ga[l + 1], dstsize=sz); lb = gb[l] - cv2.pyrUp(gb[l + 1], dstsize=sz)
        out = cv2.pyrUp(out, dstsize=sz) + la * (1 - gm[l][..., None]) + lb * gm[l][..., None]
    return out

stats_prev = None

c = av.open(cfg["master"]); st = c.streams.video[0]
enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
    "-ss", str(cfg["t0"]), "-t", str(cfg["t1"] - cfg["t0"] + 1 / fps), "-i", cfg["master"], "-map", "0:v", "-map", "1:a",
    "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
    "-c:a", "copy", "-shortest", cfg["out"]], stdin=subprocess.PIPE)
crop_feather = np.zeros((512, 512), np.float32); cv2.rectangle(crop_feather, (12, 12), (499, 499), 1.0, -1)
crop_feather = cv2.GaussianBlur(crop_feather, (0, 0), 8)
# zona válida del recorte con un desvanecido amplio en el borde inferior (el cuello sale del recorte por abajo)
crop_valid = crop_feather * (1 - smoothstep(440, 505, np.mgrid[0:512, 0:512][0].astype(np.float32)))
dbg = set(cfg.get("debugFrames", [])); nout = 0
for i, fr in enumerate(c.decode(st)):
    t = i / fps
    if t < cfg["t0"] - 1e-6: continue
    if t > cfg["t1"] + 1e-6: break
    F = fr.to_ndarray(format="rgb24").astype(np.float32) / 255
    f = info.get(i)
    if f and f.get("ok"):
        src_idx = i + int(round(cfg["src_offset"] * fps))
        A = cv2.imread(os.path.join(cfg["alpha_dir"], f"alpha_{src_idx:05d}.png"), 0).astype(np.float32) / 255
        bg = next((b for a_, z_, b in bgr if a_ <= src_idx <= z_), bg0)
        yc, fh = f["chin"][1], f["face_h"]
        # 1) quitar la cabeza original (incluido el pelo) → fondo de estudio exacto
        cx = f["chin"][0]
        # anchura real del cuello original (alfa de persona + piel) a 0,22·cara bajo el mentón
        ry = int(min(H - 1, yc + 0.22 * fh)); row = (A[ry] > 0.6) & (skin_mask(F[ry:ry + 1])[0] > 0.3)
        xs = np.where(row[int(max(0, cx - 0.6 * fh)):int(min(W, cx + 0.6 * fh))])[0]
        hw = float(np.clip((xs.max() - xs.min()) / 2 if len(xs) > 5 else 0.28 * fh, 0.22 * fh, 0.45 * fh))
        col_old = 1 - smoothstep(hw - 0.02 * fh, hw + 0.04 * fh, np.abs(xx - cx))   # cuello original completo (no hombros)
        below = smoothstep(yc - 0.02 * fh, yc + 0.08 * fh, yy)            # 0 por encima del mentón, 1 por debajo
        # 2) cabeza nueva al fotograma
        n = f["n"]; G = cv2.cvtColor(cv2.imread(os.path.join(cfg["lp_dir"], "gen", f"gen_{n:05d}.png")), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        ag = cv2.imread(os.path.join(cfg["gen_alpha_dir"], f"alpha_{n:05d}.png"), 0).astype(np.float32) / 255
        # descontaminación del borde (cabello): quita el color del fondo del retrato generado
        wb = (ag < 0.03).astype(np.float32)
        Bo = cv2.GaussianBlur(G * wb[..., None], (0, 0), 15) / (cv2.GaussianBlur(wb, (0, 0), 15)[..., None] + 1e-4)
        e = (ag > 0.03) & (ag < 0.97); a3 = ag[..., None]
        G[e] = np.clip((G[e] - (1 - a3[e]) * Bo[e]) / np.maximum(a3[e], 0.15), 0, 1)
        ag = ag * crop_feather
        M = np.array(f["M_c2o"], np.float32)[:2]
        sc = float(np.hypot(M[0, 0], M[0, 1]))  # escala recorte→fotograma
        if sc > 1.05:  # cara ampliada (primer plano): enfoque suave proporcional
            G = np.clip(G + min(0.6, 0.45 * (sc - 1)) * (G - cv2.GaussianBlur(G, (0, 0), 1.2)), 0, 1)
        Gw = cv2.warpAffine(G, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
        Aw = cv2.warpAffine(ag, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        Vw = cv2.warpAffine(crop_valid, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        # 3) cuello nuevo: cubre por completo el cuello original y baja hasta el escote
        col_new = 1 - smoothstep(hw + 0.03 * fh, hw + 0.10 * fh, np.abs(xx - cx))
        N = Aw * ((1 - below) + below * col_new * Vw)
        # bajo el mentón el cuello nuevo es opaco dentro de su columna (la sombra del mentón no debe dejar ver el fondo)
        neckzone = col_new * Vw * smoothstep(yc - 0.12 * fh, yc - 0.02 * fh, yy)
        N = np.maximum(N, neckzone * np.clip(Aw * 3, 0, 1))
        # retirar la cabeza original; en el cuello, solo donde la nueva cubre del todo (Vw≈1)
        # justo encima del mentón (franja de mandíbula) solo se retira lo que la cabeza nueva cubre: evita huecos junto al cuello
        jaw = smoothstep(yc - 0.16 * fh, yc - 0.04 * fh, yy) * (1 - below)
        above = (1 - below) * (1 - jaw) + jaw * np.maximum(col_old, np.clip(Aw * 1.5, 0, 1))
        # bajo el mentón NO se retira el cuello original: el nuevo (ya con el mismo tono) se superpone encima,
        # así nunca puede asomar el fondo en la unión
        Hm = A * above
        # regla: en la zona del cuello/mandíbula nunca se retira más del original de lo que cubre la cabeza nueva
        nz = smoothstep(yc - 0.2 * fh, yc - 0.1 * fh, yy)
        Hm = Hm * (1 - nz) + np.minimum(Hm, N) * nz
        F1 = F * (1 - Hm[..., None]) + (bg + rng.normal(0, 1.3 / 255, bg.shape).astype(np.float32)) * Hm[..., None]
        # 4) piel unificada: transferencia Lab (media y desviación) de la piel nueva hacia la piel real del cuerpo
        bodyreg = (A > 0.95) & (yy > yc + 0.35 * fh) & (yy < yc + 1.1 * fh) & (np.abs(xx - cx) < 0.45 * fh)
        sk_old = skin_mask(F) * bodyreg
        sk_new = skin_mask(Gw) * (Aw > 0.95) * (yy < yc + 0.30 * fh)
        if sk_old.sum() > 300 and sk_new.sum() > 300:
            Lo, Ln = lab(F), lab(Gw)
            wo, wn = sk_old[..., None], sk_new[..., None]
            mo = (Lo * wo).sum((0, 1)) / wo.sum(); mn = (Ln * wn).sum((0, 1)) / wn.sum()
            so = np.sqrt(((Lo - mo) ** 2 * wo).sum((0, 1)) / wo.sum()); sn = np.sqrt(((Ln - mn) ** 2 * wn).sum((0, 1)) / wn.sum())
            st_ = np.concatenate([mo, mn, so, sn])
            stats_prev = st_ if (stats_prev is None or f.get("cut")) else 0.85 * stats_prev + 0.15 * st_
        if stats_prev is not None:
            mo, mn, so, sn = stats_prev[0:3], stats_prev[3:6], stats_prev[6:9], stats_prev[9:12]
            Ln = lab(Gw); ratio = 1 + 0.5 * (np.clip(so / np.maximum(sn, 1e-3), 0.7, 1.4) - 1)   # contraste a medias: conserva textura
            Lt = (Ln - mn) * ratio + mo
            k = cfg.get("skinMatch", 0.95) * np.clip(skin_mask(Gw) * 1.15, 0, 1)[..., None]  # pelo, ojos y fondo casi intactos
            Lt[..., 0] = Ln[..., 0] + (Lt[..., 0] - Ln[..., 0]) * 0.85  # luminancia: 85 % (luz del set)
            Gw = rgb_from_lab(Ln * (1 - k) + Lt * k)
        comp = F1 * (1 - N[..., None]) + Gw * N[..., None]
        # 5) costura del cuello invisible: mezcla multibanda en la franja de unión
        y0b, y1b = int(max(0, yc - 0.05 * fh)), int(min(H, yc + 0.75 * fh)); x0b, x1b = int(max(0, cx - hw - 0.2 * fh)), int(min(W, cx + hw + 0.2 * fh))
        if y1b - y0b > 32 and x1b - x0b > 32:
            mb = N[y0b:y1b, x0b:x1b] * col_new[y0b:y1b, x0b:x1b]
            pb = pyr_blend(F1[y0b:y1b, x0b:x1b], Gw[y0b:y1b, x0b:x1b], mb, 4)
            wband = (smoothstep(yc - 0.02 * fh, yc + 0.08 * fh, yy) * col_new)[y0b:y1b, x0b:x1b][..., None]
            comp[y0b:y1b, x0b:x1b] = comp[y0b:y1b, x0b:x1b] * (1 - wband) + np.clip(pb, 0, 1) * wband
        F = comp
        if i in dbg:
            cv2.imwrite(os.path.join(os.path.dirname(cfg["out"]), f"ia_debug_{i:05d}.png"), cv2.cvtColor((np.clip(F, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    enc.stdin.write((np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()); nout += 1
    if nout % 60 == 0: print("fotogramas", nout, flush=True)
enc.stdin.close(); enc.wait(); print("listo", nout, "→", cfg["out"])
