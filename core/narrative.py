def build_narrative(scene, vehicles, persons, analysis):
    """
    Generates an investigator-style narrative reconstruction
    """

    lines = []

    # Opening
    lines.append(
        "Based on visual evidence analysis, the incident appears to involve "
        f"{len(vehicles)} motor vehicle(s) "
        f"in a {analysis['severity']['level'].lower()}-severity collision."
    )

    # Collision type
    lines.append(
        f"The collision is classified as a {scene['collision_type'].lower()}, "
        "based on spatial overlap and object interaction patterns."
    )

    # Vehicle responsibility
    primary = analysis["fault_allocation"]["primary_vehicle"]
    if primary:
        lines.append(
            f"{primary} exhibits dominant fault indicators, "
            "including positional overlap and impact alignment "
            "consistent with active motion at the time of collision."
        )

    # Pedestrian presence
    if persons:
        lines.append(
            f"{len(persons)} pedestrian(s) were detected in the scene, "
            "which increases overall risk severity. "
            "No direct pedestrian impact is visually confirmed."
        )

    # Closing
    lines.append(
        "All conclusions are derived from visual evidence and probabilistic reasoning. "
        "This reconstruction represents an AI-assisted forensic assessment."
    )

    return " ".join(lines)