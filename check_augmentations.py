import os
import cv2
import sys
import shutil
import traceback
import albumentations as A

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

from app.core.augmentation_engine import load_filters

TESTED_DIR = "Filter_Showcase"
IMG_PATH = "img_1.png"
TXT_PATH = "img_1.txt"

def load_data():
    if not os.path.exists(IMG_PATH):
        print(f"Error: {IMG_PATH} not found.")
        sys.exit(1)
    
    image = cv2.imread(IMG_PATH)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    bboxes = []
    class_labels = []
    
    if os.path.exists(TXT_PATH):
        with open(TXT_PATH, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(float(parts[0]))
                    cx, cy, w, h = map(float, parts[1:5])
                    bboxes.append([cx, cy, w, h])
                    class_labels.append(class_id)
                    
    return image, bboxes, class_labels

def main():
    if os.path.exists(TESTED_DIR):
        shutil.rmtree(TESTED_DIR)
    os.makedirs(TESTED_DIR)
    
    image, bboxes, class_labels = load_data()
    filters = load_filters()
    
    print(f"Found {len(filters)} filters.")
    
    results = []
    
    for name, cls in filters.items():
        print(f"Testing {name}...", end="")
        try:
            # Instantiate filter - ensure it's always applied
            effect = cls(probability=1.0, enabled=True)
            
            # Create a simple pipeline with just this effect
            transform = A.Compose([
                effect.get_transform()
            ], bbox_params=A.BboxParams(
                format='yolo',
                label_fields=['class_labels'],
                min_visibility=0.0
            ))
            
            aug = transform(image=image, bboxes=bboxes, class_labels=class_labels)
            
            res_img = aug['image']
            res_img = cv2.cvtColor(res_img, cv2.COLOR_RGB2BGR)
            
            # Draw bboxes for visualization
            for bbox in aug['bboxes']:
                cx, cy, w, h = bbox
                H, W = res_img.shape[:2]
                x1 = int((cx - w/2) * W)
                y1 = int((cy - h/2) * H)
                x2 = int((cx + w/2) * W)
                y2 = int((cy + h/2) * H)
                cv2.rectangle(res_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            out_path = os.path.join(TESTED_DIR, f"{name}.png")
            cv2.imwrite(out_path, res_img)
            
            print(" OK")
            results.append((name, "OK"))
            
        except Exception as e:
            print(" FAILED")
            print(f"  Error: {e}")
            # traceback.print_exc()
            results.append((name, f"FAILED: {e}"))

    print("\nSummary:")
    for name, status in results:
        print(f"{name}: {status}")

if __name__ == "__main__":
    main()
