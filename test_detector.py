import cv2
from core.detector import Detector

det = Detector("models/yolo/yolov8m.pt")

img = cv2.imread("data/samples/s1.jpg")  # put any accident image here
res = det.detect(img)

print("\nDETECTIONS:")
for o in res:
    print(o)
