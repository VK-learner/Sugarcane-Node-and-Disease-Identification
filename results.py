from ultralytics import YOLO
import cv2
import os
import glob

# -------------------------------
# User Inputs
# -------------------------------
test_images_dir = "E:/Vaibhav/test/images"
test_labels_dir = "E:/Vaibhav/test/labels"
results_dir = "E:/Vaibhav/yolov8-results/evaluation_results"

model_path = "E:/Vaibhav/yolov8-results/My-Model-yolov8n/weights/best.pt"

threshold = 0.25      # Confidence threshold to reduce false negatives
iou_threshold = 0.5   # IoU threshold for matching boxes

os.makedirs(results_dir, exist_ok=True)

# -------------------------------
# Load Model
# -------------------------------
model = YOLO(model_path)

# -------------------------------
# IoU Function
# -------------------------------
def compute_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2]-box1[0]) * (box1[3]-box1[1])
    box2_area = (box2[2]-box2[0]) * (box2[3]-box2[1])
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area != 0 else 0

# -------------------------------
# Initialize Metrics
# -------------------------------
total_TP = 0
total_FN = 0
total_FP = 0

# -------------------------------
# Process Each Image
# -------------------------------
image_paths = glob.glob(os.path.join(test_images_dir, "*.jpg"))  # Adjust extension if needed

for img_path in image_paths:
    img_name = os.path.basename(img_path)
    label_path = os.path.join(test_labels_dir, img_name.replace(".jpg", ".txt"))

    img = cv2.imread(img_path)
    H, W, _ = img.shape
    results = model(img)[0]

    # Predicted Boxes
    pred_boxes = []
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        if score > threshold:
            pred_boxes.append([int(x1), int(y1), int(x2), int(y2)])

    # Ground Truth Boxes
    annotations = []
    with open(label_path, 'r') as file:
        for line in file.readlines():
            values = line.split()
            label = int(values[0])
            x, y, w, h = map(float, values[1:])
            x1 = int((x - w / 2) * W)
            y1 = int((y - h / 2) * H)
            x2 = int((x + w / 2) * W)
            y2 = int((y + h / 2) * H)
            annotations.append((label, [x1, y1, x2, y2]))

    # Compare Boxes
    TP = 0
    FN = 0
    FP = 0
    matched_pred = []
    img_visual = img.copy()

    for gt_label, gt_box in annotations:
        match_found = False
        for idx, pred_box in enumerate(pred_boxes):
            iou = compute_iou(gt_box, pred_box)
            if iou > iou_threshold:
                TP += 1
                match_found = True
                matched_pred.append(idx)
                cv2.rectangle(img_visual, (gt_box[0], gt_box[1]), (gt_box[2], gt_box[3]), (0, 255, 0), 2)
                cv2.putText(img_visual, "TP", (gt_box[0], gt_box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                break
        if not match_found:
            FN += 1
            cv2.rectangle(img_visual, (gt_box[0], gt_box[1]), (gt_box[2], gt_box[3]), (0, 0, 255), 2)
            cv2.putText(img_visual, "FN", (gt_box[0], gt_box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    for idx, pred_box in enumerate(pred_boxes):
        if idx not in matched_pred:
            FP += 1
            cv2.rectangle(img_visual, (pred_box[0], pred_box[1]), (pred_box[2], pred_box[3]), (0, 255, 255), 2)
            cv2.putText(img_visual, "FP", (pred_box[0], pred_box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)

    # Save visualized image
    cv2.imwrite(os.path.join(results_dir, img_name), img_visual)

    # Update totals
    total_TP += TP
    total_FN += FN
    total_FP += FP

# -------------------------------
# Calculate Overall Metrics
# -------------------------------
recall = total_TP / (total_TP + total_FN) if (total_TP + total_FN) > 0 else 0
precision = total_TP / (total_TP + total_FP) if (total_TP + total_FP) > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print("========== MODEL EVALUATION ==========")
print(f"Total True Positives (TP): {total_TP}")
print(f"Total False Negatives (FN): {total_FN}")
print(f"Total False Positives (FP): {total_FP}")
print(f"Recall: {recall*100:.2f}%")
print(f"Precision: {precision*100:.2f}%")
print(f"F1-Score: {f1_score*100:.2f}%")
print(f"Visualized results saved to: {results_dir}") 