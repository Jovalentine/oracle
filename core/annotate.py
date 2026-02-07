import cv2

def draw_annotations(img, objects, fault_map, vehicle_indices):
    out = img.copy()
    for idx, o in enumerate(objects):
        x1,y1,x2,y2 = map(int, o["box"])
        color = (0,255,0) if o["name"]!="person" else (0,128,255)
        cv2.rectangle(out, (x1,y1), (x2,y2), color, 2)
        label = f'{o["name"]} {o["conf"]:.2f}'
        if idx in vehicle_indices and idx in fault_map:
            label += f' | fault {fault_map[idx]}%'
        cv2.putText(out, label, (x1, max(20, y1-8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return out
