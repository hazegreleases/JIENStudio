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

# --- Base Class ---

class AugmentationEffect(ABC):
    """Abstract base class for all augmentation effects."""
    
    def __init__(self, probability=0.5, enabled=True):
        self.probability = probability
        self.enabled = enabled
        self.name = self.__class__.__name__

    @abstractmethod
    def get_transform(self):
        """Return the Albumentations transform for this effect."""
        pass

    @abstractmethod
    def get_params(self):
        """Return dictionary of parameters for UI configuration."""
        pass

    @abstractmethod
    def set_params(self, params):
        """Set parameters from UI configuration."""
        pass

    def to_dict(self):
        """Serialize to dictionary."""
        data = self.get_params()
        data['type'] = self.__class__.__name__
        data['probability'] = self.probability
        data['enabled'] = self.enabled
        return data

    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary."""
        # This will be handled by a factory method mostly
        pass


# --- Effect Implementations ---

class HorizontalFlipEffect(AugmentationEffect):
    def get_transform(self):
        return A.HorizontalFlip(p=self.probability)

    def get_params(self):
        return {}

    def set_params(self, params):
        pass

class VerticalFlipEffect(AugmentationEffect):
    def get_transform(self):
        return A.VerticalFlip(p=self.probability)

    def get_params(self):
        return {}

    def set_params(self, params):
        pass

class RotateEffect(AugmentationEffect):
    def __init__(self, limit=15, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.limit = limit

    def get_transform(self):
        return A.Rotate(limit=self.limit, p=self.probability, border_mode=cv2.BORDER_CONSTANT)

    def get_params(self):
        return {'limit': self.limit}

    def set_params(self, params):
        if 'limit' in params: self.limit = int(params['limit'])

class BlurEffect(AugmentationEffect):
    def __init__(self, blur_limit=7, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.blur_limit = blur_limit

    def get_transform(self):
        # blur_limit must be odd
        limit = self.blur_limit if self.blur_limit % 2 != 0 else self.blur_limit + 1
        return A.Blur(blur_limit=limit, p=self.probability)

    def get_params(self):
        return {'blur_limit': self.blur_limit}

    def set_params(self, params):
        if 'blur_limit' in params: self.blur_limit = int(params['blur_limit'])

class GaussianNoiseEffect(AugmentationEffect):
    def __init__(self, var_limit_min=10.0, var_limit_max=50.0, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.var_limit_min = var_limit_min
        self.var_limit_max = var_limit_max

    def get_transform(self):
        return A.GaussNoise(var_limit=(self.var_limit_min, self.var_limit_max), p=self.probability)

    def get_params(self):
        return {'var_limit_min': self.var_limit_min, 'var_limit_max': self.var_limit_max}

    def set_params(self, params):
        if 'var_limit_min' in params: self.var_limit_min = float(params['var_limit_min'])
        if 'var_limit_max' in params: self.var_limit_max = float(params['var_limit_max'])

class BrightnessContrastEffect(AugmentationEffect):
    def __init__(self, brightness_limit=0.2, contrast_limit=0.2, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.brightness_limit = brightness_limit
        self.contrast_limit = contrast_limit

    def get_transform(self):
        return A.RandomBrightnessContrast(
            brightness_limit=self.brightness_limit,
            contrast_limit=self.contrast_limit,
            p=self.probability
        )

    def get_params(self):
        return {'brightness_limit': self.brightness_limit, 'contrast_limit': self.contrast_limit}

    def set_params(self, params):
        if 'brightness_limit' in params: self.brightness_limit = float(params['brightness_limit'])
        if 'contrast_limit' in params: self.contrast_limit = float(params['contrast_limit'])

class RandomCropEffect(AugmentationEffect):
    def __init__(self, height_fraction=0.8, width_fraction=0.8, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.height_fraction = height_fraction
        self.width_fraction = width_fraction

    def get_transform(self):
        # Calculate target size based on standard 640x640 YOLO input
        # This ensures consistent output size even if crop varies
        target_h = int(640 * self.height_fraction)
        target_w = int(640 * self.width_fraction)
        
        # RandomSizedBBoxSafeCrop crops a region containing bboxes and resizes to target_h/w
        return A.RandomSizedBBoxSafeCrop(
            height=target_h, 
            width=target_w, 
            erosion_rate=0.0, 
            p=self.probability
        )

    def get_params(self):
        return {'height_fraction': self.height_fraction, 'width_fraction': self.width_fraction}

    def set_params(self, params):
        if 'height_fraction' in params: self.height_fraction = float(params['height_fraction'])
        if 'width_fraction' in params: self.width_fraction = float(params['width_fraction'])

class RGBShiftEffect(AugmentationEffect):
    def __init__(self, r_shift=20, g_shift=20, b_shift=20, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.r_shift = r_shift
        self.g_shift = g_shift
        self.b_shift = b_shift

    def get_transform(self):
        return A.RGBShift(r_shift_limit=self.r_shift, g_shift_limit=self.g_shift, b_shift_limit=self.b_shift, p=self.probability)
    
    def get_params(self):
        return {'r_shift': self.r_shift, 'g_shift': self.g_shift, 'b_shift': self.b_shift}
    
    def set_params(self, params):
        if 'r_shift' in params: self.r_shift = int(params['r_shift'])
        if 'g_shift' in params: self.g_shift = int(params['g_shift'])
        if 'b_shift' in params: self.b_shift = int(params['b_shift'])

# --- Factory ---

EFFECT_REGISTRY = {
    'HorizontalFlipEffect': HorizontalFlipEffect,
    'VerticalFlipEffect': VerticalFlipEffect,
    'RotateEffect': RotateEffect,
    'BlurEffect': BlurEffect,
    'GaussianNoiseEffect': GaussianNoiseEffect,
    'BrightnessContrastEffect': BrightnessContrastEffect,
    'RandomCropEffect': RandomCropEffect,
    'RGBShiftEffect': RGBShiftEffect
}

def create_effect_from_dict(data):
    effect_type = data.get('type')
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
