"""
Modular Augmentation Engine.
Replaces the old fixed configuration with a pipeline of effect objects.
"""

import os
import cv2
import numpy as np
import albumentations as A
import json
from datetime import datetime
from abc import ABC, abstractmethod

# --- Dynamic Loading ---

import importlib.util
import inspect

def load_filters():
    """Recursively load AugmentationEffect subclasses from the filters directory."""
    registry = {}
    
    # Base directory for filters
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filters_dir = os.path.join(base_dir, 'augmentation', 'filters')
    
    if not os.path.exists(filters_dir):
        print(f"Warning: Filters directory not found at {filters_dir}")
        return registry

    # Walk through directory
    for root, dirs, files in os.walk(filters_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                
                try:
                    # Dynamic import
                    spec = importlib.util.spec_from_file_location(f"filter_module_{file}", file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Inspect for subclasses
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and obj.__module__ == module.__name__:
                            # Check if it inherits from AugmentationEffect (without importing base blindly)
                            # We can check base class name or importing base safely
                            if hasattr(obj, 'get_transform') and hasattr(obj, 'to_dict'):
                                registry[name] = obj
                                
                except Exception as e:
                    print(f"Error loading filter {file_path}: {e}")
                    
    return registry

EFFECT_REGISTRY = load_filters()

def create_effect_from_dict(data):
    effect_type = data.get('type')
    # Refresh registry on creation attempt to support hot-loading (optional, but requested)
    global EFFECT_REGISTRY
    
    if effect_type in EFFECT_REGISTRY:
        effect_cls = EFFECT_REGISTRY[effect_type]
        effect = effect_cls(probability=data.get('probability', 0.5), enabled=data.get('enabled', True))
        effect.set_params(data)
        return effect
    
    # Try reloading if not found
    EFFECT_REGISTRY = load_filters()
    if effect_type in EFFECT_REGISTRY:
        effect_cls = EFFECT_REGISTRY[effect_type]
        effect = effect_cls(probability=data.get('probability', 0.5), enabled=data.get('enabled', True))
        effect.set_params(data)
        return effect
        
    return None

# --- Pipeline ---

class AugmentationPipeline:
    def __init__(self):
        self.effects = []
        self.enabled = True
        self.augmentations_per_image = 5

    def add_effect(self, effect):
        self.effects.append(effect)

    def remove_effect(self, index):
        if 0 <= index < len(self.effects):
            self.effects.pop(index)

    def move_effect(self, from_index, to_index):
        if 0 <= from_index < len(self.effects) and 0 <= to_index < len(self.effects):
            self.effects.insert(to_index, self.effects.pop(from_index))

    def get_compose(self):
        """Compile the pipeline into an Albumentations Compose object."""
        transforms = []
        for effect in self.effects:
            if effect.enabled:
                transforms.append(effect.get_transform())
        
        return A.Compose(transforms, bbox_params=A.BboxParams(
            format='yolo',
            label_fields=['class_labels'],
            min_visibility=0.3
        ))

    def to_dict(self):
        return {
            'enabled': self.enabled,
            'augmentations_per_image': self.augmentations_per_image,
            'effects': [effect.to_dict() for effect in self.effects]
        }

    def from_dict(self, data):
        self.enabled = data.get('enabled', True)
        self.augmentations_per_image = data.get('augmentations_per_image', 5)
        self.effects = []
        for effect_data in data.get('effects', []):
            effect = create_effect_from_dict(effect_data)
            if effect:
                self.effects.append(effect)

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    def load(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                self.from_dict(data)

    def run_on_image(self, image, bboxes, class_labels):
        """Run pipeline on a single image and return transformed results."""
        if not self.enabled or not self.effects:
            return image, bboxes, class_labels

        transform = self.get_compose()
        
        # Albumentations expects specific formats
        # bboxes: [[x_center, y_center, width, height], ...] (if format is 'yolo')
        
        try:
            # Albumentations requires bboxes to be a list, even if empty
            # If bboxes is empty, we must pass empty list
            kwargs = {
                'image': image,
                'bboxes': bboxes if bboxes else [],
                'class_labels': class_labels if class_labels else []
            }
            
            # If there are no bboxes, we might need to handle it differently depending on A.Compose setup
            # But we set bbox_params, so it expects bboxes.
            if not bboxes:
                # If no bounding boxes, we still need to satisfy the Compose requirement if bbox_params are set
                # Actually, if we pass empty list it should be fine.
                pass

            result = transform(**kwargs)
            return result['image'], result['bboxes'], result['class_labels']
        except Exception as e:
            print(f"Augmentation error: {e}")
            return image, bboxes, class_labels

# --- Engine ---

class AugmentationEngine:
    """Refactored backbone using the pipeline."""
    
    def __init__(self, pipeline=None):
        self.pipeline = pipeline or AugmentationPipeline()

    def augment_dataset(self, images_dir, labels_dir, output_images_dir, output_labels_dir, progress_callback=None):
        """
        Augment entire dataset.
        """
        if not self.pipeline.enabled:
            return 0
        
        # Ensure output directories exist
        os.makedirs(output_images_dir, exist_ok=True)
        os.makedirs(output_labels_dir, exist_ok=True)
        
        # Get list of images
        image_files = [f for f in os.listdir(images_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        total_images = len(image_files)
        augmented_count = 0
        
        for idx, img_file in enumerate(image_files):
            img_path = os.path.join(images_dir, img_file)
            label_file = os.path.splitext(img_file)[0] + '.txt'
            label_path = os.path.join(labels_dir, label_file)
            
            # Load source
            image = cv2.imread(img_path)
            if image is None: continue
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            bboxes = []
            class_labels = []
            
            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            cx, cy, w, h = map(float, parts[1:5])
                            bboxes.append([cx, cy, w, h])
                            class_labels.append(class_id)
            
            # Generate augmentations
            for aug_idx in range(self.pipeline.augmentations_per_image):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                base_name = os.path.splitext(img_file)[0]
                ext = os.path.splitext(img_file)[1]
                
                aug_img_name = f"aug_{aug_idx}_{timestamp}_{base_name}{ext}"
                aug_label_name = f"aug_{aug_idx}_{timestamp}_{base_name}.txt"
                
                aug_img_path = os.path.join(output_images_dir, aug_img_name)
                aug_label_path = os.path.join(output_labels_dir, aug_label_name)
                
                # Run Pipeline
                aug_img, aug_bboxes, aug_classes = self.pipeline.run_on_image(image, bboxes, class_labels)
                
                # Save results
                final_img = cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR)
                cv2.imwrite(aug_img_path, final_img)
                
                with open(aug_label_path, 'w') as f:
                    for bbox, class_id in zip(aug_bboxes, aug_classes):
                        cx, cy, w, h = bbox
                        f.write(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
                
                augmented_count += 1
                
                if progress_callback:
                    current = idx * self.pipeline.augmentations_per_image + aug_idx + 1
                    total = total_images * self.pipeline.augmentations_per_image
                    progress_callback(current, total, f"Augmenting {img_file}")
                    
        return augmented_count

    def preview_augmentation(self, image_path, label_path):
        """Preview helper."""
        image = cv2.imread(image_path)
        if image is None: return None
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        bboxes = []
        class_labels = []
        
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        cx, cy, w, h = map(float, parts[1:5])
                        bboxes.append([cx, cy, w, h])
                        class_labels.append(class_id)
                        
        aug_img, aug_bboxes, aug_classes = self.pipeline.run_on_image(image, bboxes, class_labels)
        return aug_img, aug_bboxes, aug_classes
