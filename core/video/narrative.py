# core/video/narrative.py

def build_video_narrative(timeline, aggregation):
    """
    Constructs a forensic narrative from the timeline list and aggregation data.
    """
    
    # 1. Summarize the Timeline
    # The new timeline is a LIST of events, so we filter it to find "SEVERE" events.
    severe_events = [
        t for t in timeline 
        if "escalated to SEVERE" in t.get("event", "")
    ]
    
    impact_count = len(severe_events)
    duration_str = f"across {impact_count} distinct escalation points" if impact_count > 1 else "at a specific moment of high severity"

    # 2. Get Aggregated Stats
    avg_severity = aggregation.get("avg_severity", 0)
    peak_severity = aggregation.get("peak_severity", 0)
    vehicle_faults = aggregation.get("vehicle_faults", {})

    # 3. Build the Text
    lines = [
        "Video evidence was analyzed frame-by-frame to reconstruct the sequence of events leading to the collision."
    ]

    if impact_count > 0:
        lines.append(
            f"Significant impact activity was detected {duration_str}, "
            f"indicating a critical safety event."
        )
    else:
        lines.append(
            "No severe impact events were explicitly categorized in the timeline, "
            "suggesting a lower-severity incident or near-miss scenario."
        )

    lines.append(
        f"Average severity across the incident is {avg_severity}/100, "
        f"with a peak severity of {peak_severity}."
    )

    if vehicle_faults:
        for vid, score in vehicle_faults.items():
            lines.append(
                f"{vid} demonstrates approximately {score}% fault contribution "
                "based on trajectory and proximity analysis."
            )
    else:
        lines.append("Insufficient data to assign specific vehicle fault percentages.")

    lines.append(
        "This reconstruction is derived from visual evidence and temporal consistency analysis."
    )

    return " ".join(lines)