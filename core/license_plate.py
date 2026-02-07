import cv2
import easyocr
import os
import numpy as np

# Initialize reader once
reader = easyocr.Reader(['en'], gpu=False) 

def detect_license_plates(input_data):
    """
    Universal License Plate Detector.
    Handles:
      1. Single Image (numpy array) -> for Image Pipeline
      2. List of Analyzed Frames -> for Video Pipeline
    """
    plates = []

    # CASE 1: Video Pipeline (List of Frame Results)
    if isinstance(input_data, list):
        print(f"   > Scanning {len(input_data)} video frames for plates...")
        for fr in input_data:
            path = fr.get("full_path")
            if not path or not os.path.exists(path): continue

            img = cv2.imread(path)
            if img is None: continue
            
            _run_ocr(img, plates, timestamp=fr.get("timestamp_sec", 0), frame=fr.get("frame_file"))

    # CASE 2: Image Pipeline (Single Numpy Array)
    elif isinstance(input_data, np.ndarray):
        print("   > Scanning single image for plates...")
        _run_ocr(input_data, plates)

    return plates

def _run_ocr(img, plates_list, timestamp=None, frame=None):
    """Internal helper to run EasyOCR and append valid results."""
    try:
        results = reader.readtext(img)
        for (bbox, text, conf) in results:
            text = text.replace(" ", "").upper()
            
            # Filter noise (len > 4, confidence > 0.4)
            if len(text) > 4 and conf > 0.4:
                entry = {
                    "plate": text,
                    "confidence": round(conf, 2)
                }
                # Add video-specific fields if available
                if timestamp is not None:
                    entry["timestamp_sec"] = timestamp
                if frame is not None:
                    entry["frame"] = frame
                    
                plates_list.append(entry)
    except Exception as e:
        print(f"Warning: OCR error: {e}")