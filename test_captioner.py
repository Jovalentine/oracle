import cv2
from core.captioner import Captioner

cap = Captioner("Salesforce/blip-image-captioning-base")

img = cv2.imread("data/samples/s1.jpg")
caption = cap.caption(img)

print("\nCAPTION:", caption)
