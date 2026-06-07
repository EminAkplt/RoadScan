"""
Eğitilmiş YOLOv8 modelini tarayıcıda çalışacak ONNX formatına aktarır
ve frontend/models/ altına kopyalar.

Kullanım:
    .venv\\Scripts\\python export.py
    .venv\\Scripts\\python export.py --weights runs/pothole_yolov8n/weights/best.pt --int8
"""
import argparse
import os
import shutil
import json
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="runs/pothole_yolov8n/weights/best.pt")
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--opset", type=int, default=12)
    ap.add_argument("--int8", action="store_true", help="INT8 quantization (en küçük/edge cihaz için)")
    ap.add_argument("--out", default=os.path.join("..", "frontend", "models"))
    args = ap.parse_args()

    if not os.path.exists(args.weights):
        raise SystemExit(f"Ağırlık bulunamadı: {args.weights} — önce train.py çalıştırın.")

    model = YOLO(args.weights)

    # ONNX export — NMS'i tarayıcıda (JS) yapacağız, bu yüzden nms=False
    path = model.export(
        format="onnx",
        imgsz=args.imgsz,
        opset=args.opset,
        simplify=True,
        dynamic=False,
        int8=args.int8,
    )

    os.makedirs(args.out, exist_ok=True)
    dst = os.path.join(args.out, "pothole.onnx")
    shutil.copy(path, dst)

    # Sınıf isimlerini ve giriş boyutunu frontend için yaz
    meta = {
        "input_size": args.imgsz,
        "names": model.names,            # {0: 'pothole', ...}
        "num_classes": len(model.names),
    }
    with open(os.path.join(args.out, "model_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[export] ONNX → {dst}")
    print(f"[export] Meta → {os.path.join(args.out, 'model_meta.json')}")
    print(f"[export] Sınıflar: {model.names}")


if __name__ == "__main__":
    main()
