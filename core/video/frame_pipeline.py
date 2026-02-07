import os

def analyze_frames(frames_metadata, image_pipeline):
    """
    Runs image pipeline on frames and attaches existing metadata.
    Args:
        frames_metadata (list): List of dicts {path, timestamp, index}
        image_pipeline: The core pipeline instance
    """
    results = []

    print(f"   > Analyzing {len(frames_metadata)} frames...")

    for meta in frames_metadata:
        # Run AI analysis on the image path
        # image_pipeline.run returns a dict like { "captions":..., "objects":... }
        frame_analysis = image_pipeline.run(meta["path"])

        # Attach the precise metadata we calculated during extraction
        frame_analysis["frame_index"] = meta["index"]
        frame_analysis["timestamp_sec"] = meta["timestamp"]
        frame_analysis["frame_file"] = os.path.basename(meta["path"])
        
        # Store full path for the license plate detector to use later
        frame_analysis["full_path"] = meta["path"] 

        results.append(frame_analysis)

    return results