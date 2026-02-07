

def build_explanation(caption, fault, vehicles, humans):
    if not vehicles:
        return "No vehicles detected. Forensic fault analysis could not be established."

    main_idx = max(
        range(len(fault)),
        key=lambda i: list(fault.values())[i]
    )

    main_vehicle = (
        vehicles[main_idx].get("label")
        or vehicles[main_idx].get("name", "unknown vehicle")
    )

    explanation = (
        f"The scene analysis indicates that {main_vehicle} bears the primary "
        f"responsibility based on spatial overlap, collision dynamics, and "
        f"relative positioning observed in the evidence."
    )

    if humans:
        explanation += (
            f" Presence of {len(humans)} pedestrian(s) increased the "
            f"overall severity and risk assessment."
        )

    return explanation