"""
Üç yol-hasarı veri setini TEK 4-sınıf YOLO setinde birleştirir:
  RDD2022 (Longitudinal/Transverse/Alligator/Pothole, 0-3) → olduğu gibi
  BharatPotHole (pothole=0) → çukur sınıfı 3'e çevrilir
  IVCNZ pothole (pothole=0) → çukur sınıfı 3'e çevrilir

Çıktı: merged/images/{train,val} + merged/labels/{train,val} + merged/data.yaml
Eğitim BAŞLATILMAZ; sadece veri hazırlanır.
"""
import os, zipfile, shutil, random

ROOT = os.path.dirname(os.path.abspath(__file__))
RDD_ZIP = r"C:\Users\Emin\Downloads\archive (1).zip"
RDD_RAW = os.path.join(ROOT, "rdd_raw")
BHARAT  = os.path.join(ROOT, "bharat_raw", "BharatPotHole", "BharatPotHole")
IVCNZ   = os.path.join(ROOT, "dataset_raw", "extracted")
OUT     = os.path.join(ROOT, "merged")
POTHOLE_IDX = 3
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}

NAMES = ["Longitudinal Crack", "Transverse Crack", "Alligator Crack", "Potholes"]


def ensure_dirs():
    for sp in ("train", "val"):
        os.makedirs(os.path.join(OUT, "images", sp), exist_ok=True)
        os.makedirs(os.path.join(OUT, "labels", sp), exist_ok=True)


def convert_label(text, force_class=None):
    """YOLO detect ya da segment satırlarını 'cls cx cy w h' kutularına çevirir."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        t = line.split()
        try:
            cls = int(float(t[0]))
            coords = [float(x) for x in t[1:]]
        except Exception:
            continue
        if force_class is not None:
            cls = force_class
        if cls < 0 or cls > 3:
            continue
        if len(coords) == 4:
            cx, cy, w, h = coords
        elif len(coords) >= 6 and len(coords) % 2 == 0:   # poligon → bbox
            xs, ys = coords[0::2], coords[1::2]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        else:
            continue
        if w <= 0 or h <= 0:
            continue
        out.append(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return out


counts = {"train": 0, "val": 0}


def copy_pair(img_path, lbl_text, split, prefix, force_class=None):
    idx = counts[split]
    base = f"{prefix}_{idx:06d}"
    ext = os.path.splitext(img_path)[1].lower()
    shutil.copy(img_path, os.path.join(OUT, "images", split, base + ext))
    lines = convert_label(lbl_text, force_class) if lbl_text else []
    with open(os.path.join(OUT, "labels", split, base + ".txt"), "w") as f:
        f.write("\n".join(lines))
    counts[split] += 1


def add_split_dataset(img_dir, lbl_dir, dst_split, prefix, force_class=None):
    if not os.path.isdir(img_dir):
        print(f"  ! yok: {img_dir}")
        return 0
    n = 0
    for fn in os.listdir(img_dir):
        if os.path.splitext(fn)[1].lower() not in IMG_EXT:
            continue
        ip = os.path.join(img_dir, fn)
        lp = os.path.join(lbl_dir, os.path.splitext(fn)[0] + ".txt")
        txt = open(lp, encoding="utf-8").read() if os.path.exists(lp) else ""
        copy_pair(ip, txt, dst_split, prefix, force_class)
        n += 1
    return n


def main():
    # 1) RDD2022'yi aç (gerekirse)
    if not os.path.isdir(RDD_RAW):
        print("RDD2022 açılıyor (~12GB, birkaç dakika)...")
        with zipfile.ZipFile(RDD_ZIP) as z:
            z.extractall(RDD_RAW)
    print("RDD2022 hazır.")

    ensure_dirs()

    # 2) RDD2022 (etiketler olduğu gibi 0-3)
    for s, d in (("train", "train"), ("val", "val")):
        n = add_split_dataset(os.path.join(RDD_RAW, s, "images"),
                               os.path.join(RDD_RAW, s, "labels"), d, "rdd")
        print(f"RDD {s}: {n} -> toplam {counts}")

    # 3) BharatPotHole (çukur 0 -> 3)
    for s, d in (("train", "train"), ("valid", "val")):
        n = add_split_dataset(os.path.join(BHARAT, s, "images"),
                               os.path.join(BHARAT, s, "labels"), d, "bha", POTHOLE_IDX)
        print(f"Bharat {s}: {n} -> toplam {counts}")

    # 4) IVCNZ (düz yapı, %90/10 böl, çukur 0 -> 3)
    random.seed(42)
    pairs = []
    for root, _, files in os.walk(IVCNZ):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in IMG_EXT:
                ip = os.path.join(root, fn)
                lp = os.path.splitext(ip)[0] + ".txt"
                if os.path.exists(lp):
                    pairs.append((ip, lp))
    random.shuffle(pairs)
    nval = max(1, int(len(pairs) * 0.1))
    for i, (ip, lp) in enumerate(pairs):
        d = "val" if i < nval else "train"
        copy_pair(ip, open(lp, encoding="utf-8").read(), d, "ivc", POTHOLE_IDX)
    print(f"IVCNZ: {len(pairs)} -> toplam {counts}")

    # 5) data.yaml
    with open(os.path.join(OUT, "data.yaml"), "w", encoding="utf-8") as f:
        f.write("path: " + OUT.replace("\\", "/") + "\n")
        f.write("train: images/train\nval: images/val\n")
        f.write(f"nc: 4\nnames: {NAMES}\n")

    print("\n=== BİRLEŞTİRME TAMAM ===")
    print(f"train: {counts['train']} | val: {counts['val']} | toplam: {counts['train']+counts['val']}")
    print(f"data.yaml: {os.path.join(OUT, 'data.yaml')}")


if __name__ == "__main__":
    main()
