"""Saf onnxruntime ile hızlı tespit testi (frontend pipeline'ının aynısı)."""
import glob, os, numpy as np, onnxruntime as ort
from PIL import Image

S = 640
sess = ort.InferenceSession("../frontend/models/pothole.onnx", providers=["CPUExecutionProvider"])
iname = sess.get_inputs()[0].name


def letterbox(im):
    w, h = im.size
    s = min(S / w, S / h)
    nw, nh = int(w * s), int(h * s)
    px, py = (S - nw) // 2, (S - nh) // 2
    canvas = Image.new("RGB", (S, S), (114, 114, 114))
    canvas.paste(im.resize((nw, nh)), (px, py))
    return canvas, s, px, py, w, h


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0


def detect(path, conf=0.35, iou_t=0.45):
    im = Image.open(path).convert("RGB")
    lb, s, px, py, w, h = letterbox(im)
    x = np.asarray(lb, np.float32).transpose(2, 0, 1)[None] / 255.0
    out = sess.run(None, {iname: x})[0][0]      # (5, 8400)
    out = out.T                                  # (8400, 5)
    boxes = []
    for r in out:
        sc = r[4]
        if sc < conf:
            continue
        cx, cy, bw, bh = r[0], r[1], r[2], r[3]
        x1 = (cx - bw / 2 - px) / s; y1 = (cy - bh / 2 - py) / s
        x2 = (cx + bw / 2 - px) / s; y2 = (cy + bh / 2 - py) / s
        boxes.append([x1, y1, x2, y2, float(sc)])
    boxes.sort(key=lambda b: -b[4])
    keep = []
    while boxes:
        c = boxes.pop(0); keep.append(c)
        boxes = [b for b in boxes if iou(c, b) < iou_t]
    return keep


imgs = sorted(glob.glob("dataset/images/val/*"))[:8]
total = 0
for p in imgs:
    d = detect(p)
    total += len(d)
    confs = [round(b[4], 2) for b in d]
    print(f"{os.path.basename(p)} -> {len(d)} cukur {confs}")
print("TOPLAM:", total, "| test edilen goruntu:", len(imgs))
