import cv2
import easyocr
import os

# Initialize reader once
reader = easyocr.Reader(['en'], gpu=False) 

def detect_license_plates(frame_results):
    """
    Runs OCR on analyzed frames. Reads timestamp directly from frame_results.
    """
    plates = []
    print(f"   > Scanning {len(frame_results)} frames for license plates...")

    for fr in frame_results:
        path = fr.get("full_path")
        
        if not path or not os.path.exists(path):
            continue

        img = cv2.imread(path)
        if img is None: continue

        # Run OCR
        try:
            ocr_out = reader.readtext(img)
        except:
            continue

        for (bbox, text, conf) in ocr_out:
            text = text.replace(" ", "").upper()
            
            if len(text) > 4 and conf > 0.4:
                plates.append({
                    "plate": text,
                    "confidence": round(conf, 2),
                    "timestamp_sec": fr.get("timestamp_sec", 0), # ✅ Reads existing time
                    "frame": fr.get("frame_file", os.path.basename(path)),
                    "frame_index": fr.get("frame_index", 0)
                })

    return plates