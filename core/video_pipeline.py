import os
import uuid
from datetime import datetime

# Import updated modules
from core.video.extractor import extract_frames
from core.video.frame_pipeline import analyze_frames
from core.video.license_plate import detect_license_plates
from core.video.timeline import reconstruct_timeline
from core.video.narrative import build_video_narrative
from core.video.aggregation import aggregate_video_analysis
from core.video.hash_utils import hash_frames, build_chain_of_custody

class VideoPipeline:
    def __init__(self, image_pipeline, output_dir):
        self.image_pipeline = image_pipeline
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self, video_path: str) -> dict:
        case_id = uuid.uuid4().hex[:8]
        frames_dir = os.path.join(self.output_dir, f"{case_id}_frames")
        
        # 1. EXTRACT (Returns list of {path, timestamp, index})
        frames_metadata = extract_frames(video_path, frames_dir, fps=3)

        # 2. ANALYZE (Returns list of analyzed frames with timestamps attached)
        frame_results = analyze_frames(frames_metadata, self.image_pipeline)

        # 3. DETECT PLATES (Uses analyzed frames + timestamps)
        license_plates = detect_license_plates(frame_results)

        # 4. TIMELINE & AGGREGATION
        timeline = reconstruct_timeline(frame_results)
        aggregation = aggregate_video_analysis(frame_results)

        # 5. NARRATIVE
        narrative_text = build_video_narrative(timeline, aggregation)

        # 6. CUSTODY
        # We need to recreate a simple list of paths for the hasher
        just_paths = [f["full_path"] for f in frame_results] 
        frame_hashes = hash_frames(just_paths)
        
        chain_of_custody = build_chain_of_custody(
            case_id=case_id,
            user="SYSTEM",
            video_path=video_path,
            frame_hashes=frame_hashes
        )
        
        # Prepare list of filenames for UI
        frame_filenames = [f["frame_file"] for f in frame_results]

        # 7. FINAL RETURN
        return {
            "case": {
                "case_id": case_id,
                "generated_at": datetime.utcnow().isoformat(),
                "system": "Oracle Forensic System v1.0",
                "disclaimer": "AI-assisted forensic assessment."
            },
            "scene": {
                "video_fps": 3,
                "total_frames_analyzed": len(frame_results)
            },
            "entities": {
                "vehicles": [], 
                "persons": []
            },
            "analysis": {
                "severity": {
                    "score": aggregation.get("avg_severity", 0),
                    "level": (
                        "SEVERE" if aggregation.get("avg_severity", 0) > 70 
                        else "MODERATE" if aggregation.get("avg_severity", 0) > 35 
                        else "MINOR"
                    )
                }
            },
            "evidence": {
                "video_file": video_path,
                "frames_dir": frames_dir,
                "frames": frame_filenames
            },
            "timeline": timeline,
            "narrative": { "reconstruction": narrative_text },
            "chain_of_custody": chain_of_custody,
            
            # ✅ ROOT LEVEL ACCESS FOR TEMPLATE
            "license_plates": license_plates
        }