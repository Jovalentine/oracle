import cv2
from deepface import DeepFace

# --------------------------------------------------
#     HUMAN FORENSIC ANALYSER
#     - gender detection
#     - age estimation
#     - child/adult classification
# --------------------------------------------------

class HumanAnalyser:
    def __init__(self):
        print("[HumanAnalyser] DeepFace initialized")

    def analyse(self, image, objects):
        """
        image   : OpenCV image
        objects : YOLO detections
        return  : list of human forensic profiles
        """

        humans = [o for o in objects if o["name"] == "person"]
        results = []

        for idx, h in enumerate(humans):
            x1, y1, x2, y2 = map(int, h["box"])
            face_img = image[y1:y2, x1:x2]

            profile = {
                "person_id": idx + 1,
                "box": [x1, y1, x2, y2],
                "gender": "unknown",
                "age": "unknown",
                "category": "unknown"
            }

            if face_img.size == 0:
                results.append(profile)
                continue

            try:
                analysis = DeepFace.analyze(
                    img_path = face_img,
                    actions = ["gender", "age"],
                    enforce_detection = False,
                    silent = True
                )

                gender = analysis[0]["dominant_gender"]
                age = int(analysis[0]["age"])

                profile["gender"] = gender
                profile["age"] = age

                # forensic grouping
                if age < 14:
                    profile["category"] = "child"
                elif age < 60:
                    profile["category"] = "adult"
                else:
                    profile["category"] = "senior"

            except Exception as e:
                print("[HumanAnalyser] Face analysis failed:", e)

            results.append(profile)

        return results
