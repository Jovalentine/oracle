from .geometry import iou, center, horizontal_relation

VEHICLE_NAMES = {"car", "truck", "bus", "motorcycle", "bicycle", "van"}

def is_vehicle(obj):
    return obj["name"] in VEHICLE_NAMES


def is_fallen_motorcycle(obj):
    x1, y1, x2, y2 = obj["box"]
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    return obj["name"] == "motorcycle" and (w > h * 1.2)


def impact_side(a, b):
    ax, ay = center(a["box"])
    bx, by = center(b["box"])
    # Straight head-on alignment
    if abs(ax - bx) < 50:
        return "front_or_back"
    return "right" if bx > ax else "left"


def rear_end_suspect(a, b):
    ax, ay = center(a["box"])
    bx, by = center(b["box"])
    aligned = abs(ax - bx) < 80
    b_is_behind = by > ay
    return aligned and b_is_behind


def fault_score(objects, caption: str):
    vehicles = [o for o in objects if is_vehicle(o)]
    vcount = len(vehicles)

    if vcount <= 1:
        return {0:0.0}

    score = {i: 50 for i in range(vcount)}
    caption = caption.lower()

    # ================
    #  RULE A: Remove background vehicles (no overlap with any other)
    # ================
    involved = set()
    for i in range(vcount):
        for j in range(vcount):
            if i == j:
                continue
            if iou(vehicles[i]["box"], vehicles[j]["box"]) > 0.01:
                involved.add(i)
                involved.add(j)

    # Vehicles not involved get forced score = 0 later after normalization
    uninvolved = {i for i in range(vcount) if i not in involved}

    # ================
    # RULE 1: Fallen motorcycle victim
    # ================
    for i, v in enumerate(vehicles):
        if is_fallen_motorcycle(v):
            for j in range(vcount):
                if j != i:
                    score[j] += 30
            score[i] -= 10

    # ================
    # RULE 2: Crash words
    # ================
    for w in ["crash", "collided", "impact", "wreck", "smashed", "collision"]:
        if w in caption:
            for i in score:
                score[i] += 5

    # ================
    # RULE 3: Overlap impact logic
    # ================
    for i in range(vcount):
        for j in range(i+1, vcount):
            ov = iou(vehicles[i]["box"], vehicles[j]["box"])
            if ov > 0.05:
                side = impact_side(vehicles[i], vehicles[j])
                if side == "front_or_back":
                    score[i] += 20
                    score[j] += 20
                elif side == "left":
                    score[i] += 15
                elif side == "right":
                    score[j] += 15

    # ================
    # RULE 4: Rear-end
    # ================
    for i in range(vcount):
        for j in range(vcount):
            if i == j: 
                continue
            if rear_end_suspect(vehicles[i], vehicles[j]):
                score[j] += 20

    # NORMALIZE
    vals = list(score.values())
    mn, mx = min(vals), max(vals)
    norm = {i: round(100 * (score[i] - mn) / (mx - mn + 1e-6), 1) for i in score}

    # Force uninvolved vehicles → 0%
    for i in uninvolved:
        norm[i] = 0.0

    return norm
def verification_layer(primary_fault: dict, objects: list):
    """
    Second-stage verification.
    Re-evaluates fault scores using extra evidence.
    """

    vehicles = [o for o in objects if is_vehicle(o)]
    verified = primary_fault.copy()

    # Rule 1: If motorcycle is fallen → strongly reduce its fault
    for i, v in enumerate(vehicles):
        if is_fallen_motorcycle(v):
            verified[i] = max(0, verified[i] - 30)
            for j in verified:
                if j != i:
                    verified[j] += 10

    # Rule 2: If vehicle has no overlap with any → background vehicle
    for i in range(len(vehicles)):
        involved = False
        for j in range(len(vehicles)):
            if i != j and iou(vehicles[i]["box"], vehicles[j]["box"]) > 0.01:
                involved = True
                break
        if not involved:
            verified[i] = 0

    # Rule 3: If only one strong vehicle remains → boost confidence
    max_val = max(verified.values())
    for i in verified:
        if verified[i] == max_val:
            verified[i] += 10

    return verified

def normalize_fault(fault_dict: dict):
    """
    Converts verified scores into 0–100 percentages.
    """
    if not fault_dict:
        return {}

    vals = list(fault_dict.values())
    total = sum(vals)

    if total == 0:
        return {i: 0.0 for i in fault_dict}

    norm = {i: round((fault_dict[i] / total) * 100, 1) for i in fault_dict}
    return norm
