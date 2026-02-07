from core.pipeline import Pipeline

pipe = Pipeline(
    yolo_weights="models/yolo/yolov8m.pt",
    caption_model="Salesforce/blip-image-captioning-base",
    storage_dir="data/outputs"
)

result = pipe.run("data/samples/s1.jpg")  # your accident image

print("\nCAPTION:", result["caption"])
print("\nFAULT ESTIMATION:", result["fault"])
print("\nEXPLANATION:", result["explanation"])
print("\nOUTPUT IMAGE:", result["image_out"])
