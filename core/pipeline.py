import os
import uuid
import cv2
import hashlib
from datetime import datetime

from core.detector import Detector
from core.captioner import Captioner
from core.human_analyser import HumanAnalyser
from core.reasoning import (
    fault_score,
    verification_layer,
    normalize_fault,
    is_vehicle
)
from core.annotate import draw_annotations
from core.geometry import iou
from core.explanation import build_explanation
from core.config import VEHICLE_NAMES
from core.severity import compute_severity
from core.narrative import build_narrative
# ✅ NEW IMPORT
from core.license_plate import detect_license_plates


class Pipeline:
    """
    Oracle Forensic AI Pipeline
    Produces a structured, investigator-grade forensic report schema
    """

    def __init__(self, yolo_weights, caption_model, storage_dir):
        self.detector = Detector(yolo_weights)
        self.captioner = Captioner(caption_model)
        self.human = HumanAnalyser()

        self.storage = storage_dir
        os.makedirs(self.storage, exist_ok=True)

        self._cache = {}

    def run(self, image_path: str) -> dict:
        img_hash = self._hash_image(image_path)

        # ---- cache safety ----
        if img_hash in self._cache:
            cached = self._cache[img_hash]
            if "evidence" in cached:
                return cached

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Invalid image input")

        # =================================================
        # 1. OBJECT & HUMAN DETECTION
        # =================================================

        objects = self.detector.detect(img)

        # ✅ 2. LICENSE PLATE DETECTION
        # Runs OCR on the raw image to find plates
        license_plates = detect_license_plates(img)

        persons_raw = []
        if any(o["name"] == "person" for o in objects):
            persons_raw = self.human.analyse(img, objects)

        # =================================================
        # 3. SCENE UNDERSTANDING
        # =================================================

        raw_caption = self.captioner.caption(img)
        scene_summary, max_overlap = self._scene_caption(
            objects, persons_raw, raw_caption
        )

        # =================================================
        # 4. VEHICLE FAULT REASONING
        # =================================================

        vehicle_idxs = [i for i, o in enumerate(objects) if is_vehicle(o)]

        raw_fault = fault_score(objects, scene_summary)
        verified = verification_layer(raw_fault, objects)
        normalized_fault = normalize_fault(verified)

        # =================================================
        # 5. SEVERITY ANALYSIS
        # =================================================

        severity_score = compute_severity(
            max_overlap,
            list(normalized_fault.values()),
            len(persons_raw)
        )

        severity_level = self._severity_label(severity_score)

        # =================================================
        # 6. ENTITY CONSTRUCTION
        # =================================================

        vehicles = []
        for idx, vi in enumerate(vehicle_idxs, start=1):
            percent = normalized_fault.get(idx - 1, 0.0)

            vehicles.append({
                "id": f"Vehicle-{idx}",
                "type": objects[vi]["name"],
                "bounding_box": objects[vi]["box"],
                "fault_percent": percent,
                "confidence_reason": self._confidence_reason(
                    objects[vi]["name"],
                    percent,
                    max_overlap,
                    persons_raw
                )
            })

        persons = []
        for idx, p in enumerate(persons_raw, start=1):
            persons.append({
                "id": f"Person-{idx}",
                "role": p.get("role", "pedestrian"),
                "risk_level": p.get("risk", "medium")
            })

        # =================================================
        # 7. ANNOTATED EVIDENCE
        # =================================================

        annotated = draw_annotations(
            img,
            objects,
            normalized_fault,
            vehicle_idxs
        )

        case_id = uuid.uuid4().hex[:8]
        annotated_path = os.path.join(
            self.storage, f"{case_id}_annotated.jpg"
        )
        cv2.imwrite(annotated_path, annotated)

        # =================================================
        # 8. AI INVESTIGATIVE NARRATIVE
        # =================================================

        explanation = build_explanation(
            scene_summary,
            normalized_fault,
            vehicles,
            persons
        )

        narrative_text = build_narrative(
            scene={
                "collision_type": self._collision_label(max_overlap)
            },
            vehicles=vehicles,
            persons=persons,
            analysis={
                "fault_allocation": {
                    "primary_vehicle": vehicles[0]["id"] if vehicles else None
                },
                "severity": {
                    "score": severity_score,
                    "level": severity_level
                }
            }
        )

        # =================================================
        # 9. FINAL FORENSIC SCHEMA
        # =================================================

        result = {
            "case": {
                "case_id": case_id,
                "generated_at": datetime.utcnow().isoformat(),
                "system": "Oracle Forensic System v1.0",
                "disclaimer": "AI-assisted forensic assessment."
            },

            "scene": {
                "summary": scene_summary,
                "collision_overlap": round(max_overlap, 3),
                "collision_type": self._collision_label(max_overlap)
            },

            "entities": {
                "vehicles": vehicles,
                "persons": persons
            },

            "analysis": {
                "fault_allocation": {
                    "primary_vehicle": vehicles[0]["id"] if vehicles else None,
                    "method": "Spatial overlap and object interaction reasoning"
                },
                "severity": {
                    "score": severity_score,
                    "level": severity_level
                },
                "risk_factors": {
                    "pedestrian_involved": len(persons) > 0,
                    "multi_vehicle": len(vehicles) > 1
                },
                # ✅ NEW: LICENSE PLATE RESULTS
                "license_plates": license_plates
            },
            "narrative": {
                "reconstruction": narrative_text,
                "tone": "investigative",
                "confidence": "medium"
            },
            "evidence": {
                "annotated_image": os.path.basename(annotated_path),
                "original_image": os.path.basename(image_path)
            },

            "explanation": explanation
        }

        self._cache[img_hash] = result
        return result

    # ... (Helpers) ...
    def _hash_image(self, path):
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _scene_caption(self, objects, persons, raw):
        vehicles = [o for o in objects if o["name"] in VEHICLE_NAMES]
        pieces = []
        max_overlap = 0.0

        if len(vehicles) > 1:
            pieces.append(f"{len(vehicles)} vehicles involved")
        elif len(vehicles) == 1:
            pieces.append("single vehicle present")

        for i in range(len(vehicles)):
            for j in range(i + 1, len(vehicles)):
                max_overlap = max(
                    max_overlap,
                    iou(vehicles[i]["box"], vehicles[j]["box"])
                )

        if max_overlap > 0.25:
            pieces.append("severe collision")
        elif max_overlap > 0.10:
            pieces.append("moderate collision")
        elif max_overlap > 0.02:
            pieces.append("minor contact")

        if persons:
            pieces.append(f"{len(persons)} pedestrian(s) present")

        caption = f"{raw}, with {', '.join(pieces)}." if pieces else raw
        return caption, max_overlap

    def _confidence_reason(self, label, percent, overlap, persons):
        reasons = []

        if overlap > 0.25:
            reasons.append("high-impact collision zone")
        elif overlap > 0.10:
            reasons.append("moderate collision proximity")

        if percent > 60:
            reasons.append("primary fault contributor")
        elif percent > 30:
            reasons.append("shared responsibility")

        if persons:
            reasons.append("pedestrian risk amplification")

        return ", ".join(reasons) if reasons else "insufficient visual indicators"

    def _severity_label(self, score):
        if score > 70:
            return "SEVERE"
        elif score > 35:
            return "MODERATE"
        return "MINOR"

    def _collision_label(self, overlap):
        if overlap > 0.25:
            return "High-energy collision"
        elif overlap > 0.10:
            return "Medium-energy collision"
        return "Low-energy incident"