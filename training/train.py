"""
RoadScan — YOLOv8 pothole (çukur) tespit modeli eğitimi.

Kullanım:
    .venv\\Scripts\\python train.py
    .venv\\Scripts\\python train.py --epochs 50 --model yolov8s.pt --batch 8

Çıktı: runs/<name>/weights/best.pt  → sonra export.py ile ONNX'e çevrilir.
"""
import argparse
import torch
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="dataset/data.yaml", help="data.yaml yolu")
    ap.add_argument("--model", default="yolov8n.pt", help="başlangıç ağırlığı (COCO transfer)")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--name", default="pothole_yolov8n")
    args = ap.parse_args()

    cuda = torch.cuda.is_available()
    device = 0 if cuda else "cpu"
    print(f"[train] CUDA: {cuda} | Cihaz: {torch.cuda.get_device_name(0) if cuda else 'CPU'}")
    if not cuda:
        print("[train] UYARI: GPU bulunamadı, CPU'da eğitim çok yavaş olur.")

    # COCO ön-eğitimli ağırlıktan transfer öğrenme → küçük veri setinde yüksek doğruluk
    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        patience=25,        # iyileşme durursa erken durdur
        workers=4,          # işçi sayısı düşük: bellek/pagefile güvenliği
        project="runs",
        name=args.name,
        pretrained=True,
        # hafif augmentasyon — yol/dashcam koşullarına genelleme
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        fliplr=0.5, mosaic=1.0, scale=0.5,
    )

    # Doğrulama metrikleri
    metrics = model.val()
    print(f"[train] mAP50: {metrics.box.map50:.3f} | mAP50-95: {metrics.box.map:.3f}")
    print(f"[train] En iyi ağırlık: runs/{args.name}/weights/best.pt")
    print("[train] Sonraki adım: python export.py")


if __name__ == "__main__":
    main()
