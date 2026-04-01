import numpy as np

def normalize_keypoints(keypoints, frame_w, frame_h):
    if keypoints is None:
        return None
    normalized = []
    for kp in keypoints:
        x, y, conf = kp
        nx = x / float(frame_w) if frame_w > 0 else 0.0
        ny = y / float(frame_h) if frame_h > 0 else 0.0
        normalized.append([nx, ny, conf])
    return normalized

def moving_average(sequence, window=3):
    if len(sequence) < window:
        return sequence
    return np.convolve(sequence, np.ones(window)/window, mode='valid')

def compute_centroid(bbox):
    x1, y1, x2, y2 = bbox
    return [(x1 + x2) / 2.0, (y1 + y2) / 2.0]

def compute_velocity(centroids):
    if len(centroids) < 2:
        return [0.0, 0.0]
    p1 = centroids[-2]
    p2 = centroids[-1]
    return [p2[0] - p1[0], p2[1] - p1[1]]

def euclidean_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou
