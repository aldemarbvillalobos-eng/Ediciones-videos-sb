"""Limpia las detecciones OCR de subtítulos y las convierte en eventos estables con cajas por línea.
Uso: subs_events.py <subs_boxes.json> <frame_ini> <frame_fin> <salida.json> [excluir_palabras...]
Salida: {frame_idx: [[x0,y0,x1,y1,texto],...]} para TODOS los frames del tramo."""
import sys, json, re, difflib, collections
d = {int(k): v for k, v in json.load(open(sys.argv[1])).items()}; f0, f1 = int(sys.argv[2]), int(sys.argv[3]); out = sys.argv[4]
excl = [w.upper() for w in sys.argv[5:]]
def clean(lines):
    ok = []
    for x0, y0, x1, y1, t in lines:
        words = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñü«»3]{3,}", t)
        if y0 < 875 or y1 > 1025 or (x1 - x0) < 150 or len(words) < 2 or any(e in t.upper() for e in excl): continue
        ok.append([x0, y0, x1, y1, t])
    return sorted(ok, key=lambda r: r[1])
ks = sorted(d); samples = [(k, clean(d[k])) for k in ks]
# eventos: secuencias de muestras cuyo texto se parece (o vacías)
events = []
for k, ls in samples:
    sig = " / ".join(r[4] for r in ls)
    if events and (difflib.SequenceMatcher(None, events[-1]["sig"], sig).ratio() > 0.6 or (not sig and not events[-1]["sig"])):
        events[-1]["ks"].append(k); events[-1]["all"].append(ls)
        if len(sig) > len(events[-1]["sig"]): events[-1]["sig"] = sig
    else:
        events.append({"sig": sig, "ks": [k], "all": [ls]})
res = {}
for i, e in enumerate(events):
    # por línea (agrupada por y), caja más frecuente
    rows = collections.defaultdict(list)
    for ls in e["all"]:
        for r in ls: rows[round(r[1] / 30)].append(tuple(r[:4]))
    boxes = []
    for _, bs in sorted(rows.items()):
        if len(bs) < max(1, len(e["all"]) * 0.3): continue
        x0 = min(b[0] for b in bs); x1 = max(b[2] for b in bs); y0 = collections.Counter(b[1] for b in bs).most_common(1)[0][0]
        y1 = max(collections.Counter(b[3] for b in bs).most_common(2))[0]; boxes.append([x0, y0, x1, y1])
    start = e["ks"][0] if i else f0; end = events[i + 1]["ks"][0] - 1 if i + 1 < len(events) else f1
    # el cambio real de subtítulo ocurre entre la última muestra del evento y la primera del siguiente: se toma el punto medio
    if i + 1 < len(events): end = (e["ks"][-1] + events[i + 1]["ks"][0]) // 2
    if i: start = (events[i - 1]["ks"][-1] + e["ks"][0]) // 2 + 1
    for f in range(start, end + 1): res[f] = [b + [e["sig"]] for b in boxes]
    print(f"{start}-{end}", boxes, e["sig"])
json.dump(res, open(out, "w"), ensure_ascii=False)
