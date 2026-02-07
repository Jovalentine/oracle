from ultralytics import YOLO
import numpy as np

class Detector:
    def __init__(self, weights_path: str):
        self.model = YOLO(weights_path)  # yolov8n.pt or custom fine-tuned

    def detect(self, img_bgr):
        # returns: list of dicts {cls, conf, box[x1,y1,x2,y2]}
        results = self.model.predict(source=img_bgr, verbose=False)[0]
        out = []
        for b in results.boxes:
            x1,y1,x2,y2 = b.xyxy[0].tolist()
            out.append({
                "cls": int(b.cls[0].item()),
                "name": results.names[int(b.cls[0].item())],
                "conf": float(b.conf[0].item()),
                "box": [float(x1), float(y1), float(x2), float(y2)]
            })
        return out
