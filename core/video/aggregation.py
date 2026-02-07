def aggregate_video_analysis(frame_results):
    """
    Aggregates severity scores and vehicle faults across all analyzed frames.
    """
    severities = []
    vehicle_faults = {}

    for fr in frame_results:
        # 1. Aggregate Severity
        if "analysis" in fr and "severity" in fr["analysis"]:
            severities.append(fr["analysis"]["severity"]["score"])

        # 2. Aggregate Vehicle Faults
        if "entities" in fr and "vehicles" in fr["entities"]:
            for v in fr["entities"]["vehicles"]:
                # Group by Vehicle ID (tracker_id) to average the fault score
                vid = v.get("id", "unknown")
                vehicle_faults.setdefault(vid, []).append(v.get("fault_percent", 0))

    # Calculate averages
    final_faults = {
        vid: round(sum(vals) / len(vals), 2)
        for vid, vals in vehicle_faults.items()
    }

    avg_severity = round(sum(severities) / len(severities), 1) if severities else 0
    peak_severity = max(severities) if severities else 0

    return {
        "avg_severity": avg_severity,
        "peak_severity": peak_severity,
        "vehicle_faults": final_faults
    }


def aggregate_license_plates(frame_results):
    """
    Aggregates plates with timestamps across video.
    Returns a flat list of all detections with their timing (for timeline reconstruction).
    """
    plates = []

    for fr in frame_results:
        # Check if this frame has detected plates
        for p in fr.get("license_plates", []):
            plates.append({
                "plate": p["plate"],
                "confidence": p["confidence"],
                "timestamp_sec": fr.get("timestamp_sec", 0),
                "frame_index": fr.get("frame_index", 0)
            })

    return plates