import numpy as np

def center(box):
    x1,y1,x2,y2 = box
    return ((x1+x2)/2.0, (y1+y2)/2.0)

def iou(a,b):
    ax1,ay1,ax2,ay2 = a; bx1,by1,bx2,by2 = b
    inter_x1, inter_y1 = max(ax1,bx1), max(ay1,by1)
    inter_x2, inter_y2 = min(ax2,bx2), min(ay2,by2)
    inter = max(0, inter_x2-inter_x1)*max(0, inter_y2-inter_y1)
    a_area = (ax2-ax1)*(ay2-ay1); b_area = (bx2-bx1)*(by2-by1)
    union = a_area + b_area - inter + 1e-6
    return inter/union

def horizontal_relation(a,b, tol=20):
    # returns 'left','right','overlap'
    ax = (a[0]+a[2])/2; bx = (b[0]+b[2])/2
    if abs(ax-bx) < tol: return 'overlap'
    return 'left' if ax<bx else 'right'
