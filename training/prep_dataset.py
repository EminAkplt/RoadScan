"""
Ham pothole veri setini (düz yapı: img-N.jpg + img-N.txt) YOLO eğitim
yapısına dönüştürür: dataset/images/{train,val} + dataset/labels/{train,val}
ve data.yaml üretir.

Kullanım:
    .venv\\Scripts\\python prep_dataset.py
    .venv\\Scripts\\python prep_dataset.py --zip dataset_raw/pothole.zip --val 0.15
"""
import argparse
import os
import shutil
import zipfile
import random


IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default="dataset_raw/pothole.zip")
    ap.add_argument("--extract", default="dataset_raw/extracted")
    ap.add_argument("--out", default="dataset")
    ap.add_argument("--val", type=float, default=0.15, help="doğrulama oranı")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    # 1) Aç
    if not os.path.exists(args.extract):
        print(f"[prep] Açılıyor: {args.zip}")
        with zipfile.ZipFile(args.zip) as z:
            z.extractall(args.extract)
    else:
        print(f"[prep] Zaten açılmış: {args.extract}")

    # 2) Tüm image+label çiftlerini bul (alt klasörler dahil)
    pairs = []
    class_ids = set()
    for root, _, files in os.walk(args.extract):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in IMG_EXT:
                img = os.path.join(root, fn)
                lbl = os.path.splitext(img)[0] + ".txt"
                if os.path.exists(lbl):
                    pairs.append((img, lbl))
                    # sınıf ID'lerini topla
                    try:
                        with open(lbl, "r") as f:
                            for line in f:
                                line = line.strip()
                                if line:
                                    class_ids.add(int(line.split()[0]))
                    except Exception:
                        pass

    if not pairs:
        raise SystemExit("[prep] HATA: image+label çifti bulunamadı. Zip yapısını kontrol edin.")

    print(f"[prep] {len(pairs)} adet image+label çifti bulundu.")
    print(f"[prep] Etiketlerdeki sınıf ID'leri: {sorted(class_ids)}")

    # 3) Böl
    random.seed(args.seed)
    random.shuffle(pairs)
    n_val = max(1, int(len(pairs) * args.val))
    val_pairs = pairs[:n_val]
    train_pairs = pairs[n_val:]
    print(f"[prep] train: {len(train_pairs)} | val: {len(val_pairs)}")

    # 4) Klasörleri kur ve kopyala
    for split, items in (("train", train_pairs), ("val", val_pairs)):
        img_dir = os.path.join(args.out, "images", split)
        lbl_dir = os.path.join(args.out, "labels", split)
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(lbl_dir, exist_ok=True)
        for i, (img, lbl) in enumerate(items):
            base = f"{split}_{i:05d}"
            shutil.copy(img, os.path.join(img_dir, base + os.path.splitext(img)[1].lower()))
            shutil.copy(lbl, os.path.join(lbl_dir, base + ".txt"))

    # 5) data.yaml
    # Tek sınıf varsayımı (pothole). Birden çok ID varsa uyar.
    if class_ids and max(class_ids) > 0:
        names = [f"class{i}" for i in range(max(class_ids) + 1)]
        names[0] = "pothole"
        print(f"[prep] UYARI: birden çok sınıf ID görüldü, isimleri kontrol edin: {names}")
    else:
        names = ["pothole"]

    abs_out = os.path.abspath(args.out)
    yaml_text = (
        f"path: {abs_out}\n"
        f"train: images/train\n"
        f"val: images/val\n"
        f"nc: {len(names)}\n"
        f"names: {names}\n"
    )
    with open(os.path.join(args.out, "data.yaml"), "w", encoding="utf-8") as f:
        f.write(yaml_text)

    print(f"[prep] data.yaml yazıldı:\n{yaml_text}")
    print("[prep] Sonraki adım: python train.py")


if __name__ == "__main__":
    main()
