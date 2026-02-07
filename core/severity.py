# core/severity.py

def compute_severity(max_iou, fault_values, humans_count):
    """
    Returns severity score from 0–100
    """

    severity = 0

    # Collision intensity
    if max_iou > 0.25:
        severity += 50
    elif max_iou > 0.10:
        severity += 30
    elif max_iou > 0.02:
        severity += 15

    # Fault dominance
    max_fault = max(fault_values) if fault_values else 0
    severity += max_fault * 0.4

    # Human involvement
    if humans_count > 0:
        severity += 15

    return min(int(severity), 100)