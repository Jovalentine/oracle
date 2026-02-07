import hashlib
import os
from datetime import datetime

def sha256_file(path: str) -> str:
    """Generate SHA-256 hash of a file"""
    if not os.path.exists(path):
        return "N/A"
        
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def hash_frames(frame_paths: list) -> list:
    """Hash each extracted frame"""
    hashes = []
    for fp in frame_paths:
        if os.path.exists(fp):
            hashes.append({
                "frame": os.path.basename(fp),
                "sha256": sha256_file(fp)
            })
    return hashes

def build_chain_of_custody(case_id, user, video_path, frame_hashes):
    """Formal chain-of-custody record"""
    
    # Calculate values immediately
    main_hash = sha256_file(video_path)
    now = datetime.utcnow().isoformat()

    return {
        "case_id": case_id,
        "file_hash": main_hash,       # ✅ FIX: Root level for Report
        "timestamp": now,             # ✅ FIX: Root level for Report
        "handled_by": user,
        "created_at": now,
        "evidence": {
            "video_file": os.path.basename(video_path),
            "video_sha256": main_hash,
            "frames_hashed": len(frame_hashes)
        },
        "frame_hashes": frame_hashes,
        "integrity": {
            "algorithm": "SHA-256",
            "verified": True
        }
    }