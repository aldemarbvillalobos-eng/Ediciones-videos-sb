"""Presentadora virtual: composición V3 (integración anatómica). Reutiliza la animación aprobada (lp_reenact.py).
Novedades respecto a V2 (lp_composite.py):
 1. Corrección geométrica: la cabeza nueva se escala alrededor de la frente para que su mentón coincida con el mentón
    real (la cara generada es ~6 % más corta). Escala y desplazamiento suavizados en el tiempo y por plano.
 2. Cuello anatómico: la cabeza nueva termina en la mandíbula (con su sombra bajo el mentón); desde ahí el cuello,
    los hombros y el escote son los ORIGINALES. Sin "dos zonas de piel".
 3. Color local: la piel de la cara se iguala (Lab) a la piel del cuello real justo bajo la mandíbula, por plano y estable.
 4. Iluminación: se transfiere el sombreado de baja frecuencia de la luz original a la cara nueva.
 5. Textura: se iguala el grano/detalle de la cara al de la piel real (sin filtros de belleza).
 6. Costura mandíbula-cuello con mezcla multibanda; regla "nunca retirar más de lo que se cubre".
Uso: lp_composite_v3.py <config.json>  (mismo formato que lp_composite.py; además gen_landmarks)"""
import sys, os, json, subprocess
import numpy as np, cv2, av

cfg = json.load(open(sys.argv[1])); meta = json.load(open(os.path.join(cfg["lp_dir"], "meta.json")))
gl = {int(k): v for k, v in json.load(open(os.path.join(cfg["lp_dir"], "gen_landmarks.json"))).items()}
fps = meta["fps"]; W, H = 1920, 1080
bg0 = np.load(cfg["bg"]).astype(np.float32)
bgr = [(a, b, np.load(p).astype(np.float32)) for a, b, p in cfg.get("bgRanges", [])]
info = {f["i"]: f for f in meta["frames"]}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)
off = int(round(cfg["src_offset"] * fps))

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
def skin_mask(rgb):
    ycc = cv2.cvtColor((np.clip(rgb, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2YCrCb).astype(np.float32)
    cr, cb, y = ycc[..., 1], ycc[..., 2], ycc[..., 0]
    m = smoothstep(128, 138, cr) * (1 - smoothstep(172, 182, cr)) * smoothstep(75, 85, cb) * (1 - smoothstep(128, 138, cb)) * smoothstep(40, 70, y)
    return cv2.GaussianBlur(m, (0, 0), 2)
def lab(rgb): return cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2Lab)
def rgb_from_lab(x): return np.clip(cv2.cvtColor(x.astype(np.float32), cv2.COLOR_Lab2RGB), 0, 1)
def pyr_blend(a, b, m, levels=4):
    ga, gb, gm = [a], [b], [m]
    for _ in range(levels):
        ga.append(cv2.pyrDown(ga[-1])); gb.append(cv2.pyrDown(gb[-1])); gm.append(cv2.pyrDown(gm[-1]))
    out = ga[-1] * (1 - gm[-1][..., None]) + gb[-1] * gm[-1][..., None]
    for l in range(levels - 1, -1, -1):
        sz = (ga[l].shape[1], ga[l].shape[0])
        la = ga[l] - cv2.pyrUp(ga[l + 1], dstsize=sz); lb = gb[l] - cv2.pyrUp(gb[l + 1], dstsize=sz)
        out = cv2.pyrUp(out, dstsize=sz) + la * (1 - gm[l][..., None]) + lb * gm[l][..., None]
    return out
def shot_of(i):  # plano: 1 = primer plano (según bgRanges en índice del original), 0 = plano medio
    return 1 if any(a <= i + off <= b for a, b, _ in bgr) else 0

# ---- 1) geometría: escala (alrededor de la frente nueva) y desplazamiento horizontal, suavizados por plano
idxs = sorted(i for i in info if info[i].get("ok") and i in gl)
raw = {}
for i in idxs:
    f, g = info[i], gl[i]
    top, chn = np.array(g["top"]), np.array(g["chin"])
    s = (f["chin"][1] - top[1]) / max(chn[1] - top[1], 1)
    raw[i] = (float(np.clip(s, 0.97, 1.12)), float(f["chin"][0] - chn[0]))
geo = {}
for i in idxs:
    win = [j for j in range(i - 6, i + 7) if j in raw and shot_of(j) == shot_of(i)]
    ss = np.median([raw[j][0] for j in win]); dx = np.median([raw[j][1] for j in win])
    geo[i] = (float(ss), float(np.clip(dx, -15, 15)))
# segundo pase de suavizado (media) para que la escala no tiemble
geo2 = {}
for i in idxs:
    win = [j for j in range(i - 4, i + 5) if j in geo and shot_of(j) == shot_of(i)]
    geo2[i] = (float(np.mean([geo[j][0] for j in win])), float(np.mean([geo[j][1] for j in win])))

c = av.open(cfg["master"]); st = c.streams.video[0]
enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
    "-ss", str(cfg["t0"]), "-t", str(cfg["t1"] - cfg["t0"] + 1 / fps), "-i", cfg["master"], "-map", "0:v", "-map", "1:a",
    "-c:v", "libx264", "-crf", "10", "-preset", "slow", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
    "-c:a", "copy", "-shortest", cfg["out"]], stdin=subprocess.PIPE)
crop_feather = np.zeros((512, 512), np.float32); cv2.rectangle(crop_feather, (12, 12), (499, 499), 1.0, -1)
crop_feather = cv2.GaussianBlur(crop_feather, (0, 0), 8)
state = {"shot": None, "lab": None, "grain": None, "shade": None}
dbg = set(cfg.get("debugFrames", [])); nout = 0
for i, fr in enumerate(c.decode(st)):
    t = i / fps
    if t < cfg["t0"] - 1e-6: continue
    if t > cfg["t1"] + 1e-6: break
    F = fr.to_ndarray(format="rgb24").astype(np.float32) / 255
    f = info.get(i)
    if f and f.get("ok") and i in geo2:
        sh = shot_of(i)
        if sh != state["shot"]: state.update(shot=sh, lab=None, grain=None, shade=None)  # nuevo plano: reinicia estabilizadores
        A = cv2.imread(os.path.join(cfg["alpha_dir"], f"alpha_{i + off:05d}.png"), 0).astype(np.float32) / 255
        bg = next((b for a_, z_, b in bgr if a_ <= i + off <= z_), bg0)
        yc, fh, cx = f["chin"][1], f["face_h"], f["chin"][0]
        # --- cabeza nueva con corrección geométrica
        n = f["n"]; G = cv2.cvtColor(cv2.imread(os.path.join(cfg["lp_dir"], "gen", f"gen_{n:05d}.png")), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        ag = cv2.imread(os.path.join(cfg["gen_alpha_dir"], f"alpha_{n:05d}.png"), 0).astype(np.float32) / 255
        wb = (ag < 0.03).astype(np.float32)  # descontaminación del borde del cabello
        Bo = cv2.GaussianBlur(G * wb[..., None], (0, 0), 15) / (cv2.GaussianBlur(wb, (0, 0), 15)[..., None] + 1e-4)
        e = (ag > 0.03) & (ag < 0.97); a3 = ag[..., None]
        G[e] = np.clip((G[e] - (1 - a3[e]) * Bo[e]) / np.maximum(a3[e], 0.15), 0, 1)
        ag = ag * crop_feather
        M = np.array(f["M_c2o"], np.float64)
        s_, dx = geo2[i]; top = np.array(gl[i]["top"])
        S = np.array([[s_, 0, (1 - s_) * top[0] + dx], [0, s_, (1 - s_) * top[1]], [0, 0, 1]])
        M2 = (S @ M)[:2].astype(np.float32)
        sc = float(np.hypot(M2[0, 0], M2[0, 1]))
        if sc > 1.05:  # enfoque proporcional al aumento (primer plano)
            G = np.clip(G + min(0.6, 0.45 * (sc - 1)) * (G - cv2.GaussianBlur(G, (0, 0), 1.2)), 0, 1)
        Gw = cv2.warpAffine(G, M2, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
        Aw = cv2.warpAffine(ag, M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        # --- máscaras: cabeza nueva hasta la mandíbula; cuello, hombros y escote originales
        below = smoothstep(yc - 0.02 * fh, yc + 0.06 * fh, yy)
        jaw_hw = 0.36 * fh
        col_jaw = 1 - smoothstep(jaw_hw, jaw_hw + 0.08 * fh, np.abs(xx - cx))
        under = col_jaw * (1 - smoothstep(yc + 0.04 * fh, yc + 0.13 * fh, yy))      # sombra bajo el mentón (nueva)
        N = Aw * ((1 - below) + below * under)
        Hm = A * (1 - below)                                                            # retira la cabeza original
        nz = smoothstep(yc - 0.22 * fh, yc - 0.12 * fh, yy)                              # zona mandíbula: Hm ≤ N
        Hm = Hm * (1 - nz) + np.minimum(Hm, np.maximum(N, Aw * (yy < yc))) * nz
        F1 = F * (1 - Hm[..., None]) + (bg + rng.normal(0, 1.3 / 255, bg.shape).astype(np.float32)) * Hm[..., None]
        # --- color local: piel de la cara → piel del cuello real (bajo la mandíbula)
        ref = (A > 0.95) & (yy > yc + 0.15 * fh) & (yy < yc + 0.45 * fh) & (np.abs(xx - cx) < 0.3 * fh)
        sk_o = skin_mask(F) * ref
        sk_n = skin_mask(Gw) * (Aw > 0.95) * (yy < yc - 0.05 * fh) * (yy > yc - 0.7 * fh)
        Lo, Ln = lab(F), lab(Gw)
        if sk_o.sum() > 200 and sk_n.sum() > 300:
            wo, wn = sk_o[..., None], sk_n[..., None]
            mo = (Lo * wo).sum((0, 1)) / wo.sum(); mn = (Ln * wn).sum((0, 1)) / wn.sum()
            so = np.sqrt(((Lo - mo) ** 2 * wo).sum((0, 1)) / wo.sum()); sn = np.sqrt(((Ln - mn) ** 2 * wn).sum((0, 1)) / wn.sum())
            v = np.concatenate([mo, mn, so, sn]); state["lab"] = v if state["lab"] is None else 0.92 * state["lab"] + 0.08 * v
        skn = np.clip(skin_mask(Gw) * 1.15, 0, 1)
        if state["lab"] is not None:
            mo, mn, so, sn = np.split(state["lab"], 4)
            ratio = 1 + 0.5 * (np.clip(so / np.maximum(sn, 1e-3), 0.75, 1.35) - 1)
            Lt = (Ln - mn) * ratio + mo
            Lt[..., 0] = Ln[..., 0] + (Lt[..., 0] - Ln[..., 0]) * 0.9
            k = skn[..., None]
            Ln = Ln * (1 - k) + Lt * k
        # --- iluminación: sombreado de baja frecuencia de la luz original sobre la cara nueva
        face_o = A * (1 - below) * skin_mask(F) * (yy > yc - 0.95 * fh)
        face_n = skn * (Aw > 0.9) * (1 - below)
        sig = max(4.0, fh / 7)
        Lb_o = cv2.GaussianBlur(Lo[..., 0] * face_o, (0, 0), sig) / (cv2.GaussianBlur(face_o, (0, 0), sig) + 1e-3)
        Lb_n = cv2.GaussianBlur(Ln[..., 0] * face_n, (0, 0), sig) / (cv2.GaussianBlur(face_n, (0, 0), sig) + 1e-3)
        both = (cv2.GaussianBlur(face_o, (0, 0), sig) > 0.25) & (cv2.GaussianBlur(face_n, (0, 0), sig) > 0.25)
        if both.sum() > 500:
            sh_o = Lb_o / max(Lb_o[both].mean(), 1e-3); sh_n = Lb_n / max(Lb_n[both].mean(), 1e-3)
            gain = np.where(both, np.clip(sh_o / np.maximum(sh_n, 1e-3), 0.85, 1.15), 1.0).astype(np.float32)
            gain = cv2.GaussianBlur(gain, (0, 0), sig / 2)
            state["shade"] = gain if (state["shade"] is None or state["shade"].shape != gain.shape) else 0.8 * state["shade"] + 0.2 * gain
            Ln[..., 0] = Ln[..., 0] * (1 + (state["shade"] - 1) * 0.6 * face_n)
        Gw = rgb_from_lab(Ln)
        # --- textura: grano/detalle de la piel real (luma) sobre la cara nueva
        Yo = Lo[..., 0]; Yn = Ln[..., 0]
        hp = lambda Y: Y - cv2.GaussianBlur(Y, (0, 0), 1.0)
        ro = (sk_o > 0.5); rn = (face_n > 0.5)
        if ro.sum() > 200 and rn.sum() > 300:
            go, gn = float(hp(Yo)[ro].std()), float(hp(Yn)[rn].std())
            g = np.sqrt(max(go ** 2 - gn ** 2, 0)); state["grain"] = g if state["grain"] is None else 0.9 * state["grain"] + 0.1 * g
        if state["grain"]:
            noise = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.6)
            noise *= state["grain"] / max(noise.std(), 1e-3)
            Gw = np.clip(Gw + (noise / 100.0)[..., None] * skn[..., None], 0, 1)
        comp = F1 * (1 - N[..., None]) + Gw * N[..., None]
        # --- costura mandíbula/cuello: mezcla multibanda
        y0b, y1b = int(max(0, yc - 0.25 * fh)), int(min(H, yc + 0.3 * fh)); x0b, x1b = int(max(0, cx - jaw_hw - 0.25 * fh)), int(min(W, cx + jaw_hw + 0.25 * fh))
        if y1b - y0b > 32 and x1b - x0b > 32:
            mb = N[y0b:y1b, x0b:x1b]
            pb = np.clip(pyr_blend(F1[y0b:y1b, x0b:x1b], Gw[y0b:y1b, x0b:x1b], mb, 4), 0, 1)
            wband = (smoothstep(yc - 0.12 * fh, yc - 0.03 * fh, yy) * col_jaw)[y0b:y1b, x0b:x1b][..., None]
            comp[y0b:y1b, x0b:x1b] = comp[y0b:y1b, x0b:x1b] * (1 - wband) + pb * wband
        F = comp
        if i in dbg:
            cv2.imwrite(os.path.join(os.path.dirname(cfg["out"]), f"ia3_debug_{i:05d}.png"), cv2.cvtColor((np.clip(F, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    enc.stdin.write((np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()); nout += 1
    if nout % 60 == 0: print("fotogramas", nout, flush=True)
enc.stdin.close(); enc.wait(); print("listo", nout, "→", cfg["out"])
