def reconstruct_timeline(frame_results):
    """
    Scans analyzed frames to build a chronological list of significant events.
    """
    timeline = []
    last_severity_level = "MINOR"
    
    # 1. Scan frames for changes
    for fr in frame_results:
        timestamp = fr.get("timestamp_sec", 0)
        frame_name = fr.get("frame_file", "unknown")
        
        analysis = fr.get("analysis", {})
        severity = analysis.get("severity", {})
        score = severity.get("score", 0)
        
        current_level = "SEVERE" if score > 70 else "MODERATE" if score > 35 else "MINOR"
        
        if current_level != last_severity_level:
            timeline.append({
                "timestamp_sec": timestamp,
                "frame": frame_name,
                "event": f"Severity escalated to {current_level} (Score: {score})"
            })
            last_severity_level = current_level

    # 2. FAILSAFE: Add Start/End if empty to prevent blank report tables
    if not timeline and frame_results:
        timeline.append({
            "timestamp_sec": frame_results[0].get("timestamp_sec", 0),
            "frame": frame_results[0].get("frame_file", ""),
            "event": "Video analysis started"
        })
        timeline.append({
            "timestamp_sec": frame_results[-1].get("timestamp_sec", 0),
            "frame": frame_results[-1].get("frame_file", ""),
            "event": "Video analysis ended"
        })

    return timeline