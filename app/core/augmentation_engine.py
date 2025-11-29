"""
Augmentation engine for YOLO dataset augmentation with bounding box support.
Uses Albumentations library for advanced augmentations.
"""

import os
import cv2
import numpy as np
from PIL import Image
import albumentations as A
from datetime import datetime
import random


class AugmentationConfig:
    """Configuration for augmentation settings."""
    
    def __init__(self):
        self.enabled = True
        self.augmentations_per_image = 5
        
        # Available augmentation filters with their settings
        self.filters = {
            'horizontal_flip': {'enabled': True, 'probability': 0.5},
            'vertical_flip': {'enabled': False, 'probability': 0.3},
            'rotation': {'enabled': True, 'probability': 0.7, 'limit': 15},
            'brightness_contrast': {'enabled': True, 'probability': 0.6, 'brightness_limit': 0.2, 'contrast_limit': 0.2},
            'blur': {'enabled': True, 'probability': 0.4, 'blur_limit': 5},
            'gaussian_noise': {'enabled': True, 'probability': 0.4, 'var_limit': [10.0, 50.0]},
            'hue_saturation': {'enabled': True, 'probability': 0.5, 'hue_shift_limit': 20, 'sat_shift_limit': 30},
            'random_crop': {'enabled': False, 'probability': 0.3, 'height': 0.8, 'width': 0.8},
            'scale': {'enabled': True, 'probability': 0.5, 'scale_limit': 0.2},
            'perspective': {'enabled': False, 'probability': 0.3, 'scale': 0.05},
        }
    
    def to_dict(self):
        """Convert config to dictionary for saving."""
        return {
            'enabled': self.enabled,
            'augmentations_per_image': self.augmentations_per_image,
            'filters': self.filters
        }
    
    def from_dict(self, data):
        """Load config from dictionary."""
        self.enabled = data.get('enabled', True)
        self.augmentations_per_image = data.get('augmentations_per_image', 5)
        self.filters.update(data.get('filters', {}))


class AugmentationEngine:
    """Engine for applying augmentations to images with YOLO labels."""
    
    def __init__(self, config=None):
        self.config = config or AugmentationConfig()
    
    def create_augmentation_pipeline(self):
        """Create Albumentations pipeline based on config."""
        transforms = []
        
        filters = self.config.filters
        
        # Horizontal flip
        if filters['horizontal_flip']['enabled']:
            transforms.append(A.HorizontalFlip(p=filters['horizontal_flip']['probability']))
        
        # Vertical flip
        if filters['vertical_flip']['enabled']:
            transforms.append(A.VerticalFlip(p=filters['vertical_flip']['probability']))
        
        # Rotation
        if filters['rotation']['enabled']:
            transforms.append(A.Rotate(
                limit=filters['rotation']['limit'],
                p=filters['rotation']['probability'],
                border_mode=cv2.BORDER_CONSTANT
            ))
        
        # Brightness and contrast
        if filters['brightness_contrast']['enabled']:
            transforms.append(A.RandomBrightnessContrast(
                brightness_limit=filters['brightness_contrast']['brightness_limit'],
                contrast_limit=filters['brightness_contrast']['contrast_limit'],
                p=filters['brightness_contrast']['probability']
            ))
        
        # Blur
        if filters['blur']['enabled']:
            transforms.append(A.Blur(
                blur_limit=filters['blur']['blur_limit'],
                p=filters['blur']['probability']
            ))
        
        # Gaussian noise
        if filters['gaussian_noise']['enabled']:
            var_limit = filters['gaussian_noise']['var_limit']
            # Convert to tuple if it's a list (from YAML)
            if isinstance(var_limit, list):
                var_limit = tuple(var_limit)
            transforms.append(A.GaussNoise(
                var_limit=var_limit,
                p=filters['gaussian_noise']['probability']
            ))
        
        # Hue saturation
        if filters['hue_saturation']['enabled']:
            transforms.append(A.HueSaturationValue(
                hue_shift_limit=filters['hue_saturation']['hue_shift_limit'],
                sat_shift_limit=filters['hue_saturation']['sat_shift_limit'],
                val_shift_limit=20,
                p=filters['hue_saturation']['probability']
            ))
        
        # Random crop
        if filters['random_crop']['enabled']:
            transforms.append(A.RandomSizedBBoxSafeCrop(
                height=int(640 * filters['random_crop']['height']),
                width=int(640 * filters['random_crop']['width']),
                p=filters['random_crop']['probability']
            ))
        
        # Scale
        if filters['scale']['enabled']:
            transforms.append(A.RandomScale(
                scale_limit=filters['scale']['scale_limit'],
                p=filters['scale']['probability']
            ))
        
        # Perspective
        if filters['perspective']['enabled']:
            transforms.append(A.Perspective(
                scale=filters['perspective']['scale'],
                p=filters['perspective']['probability']
            ))
        
        return A.Compose(transforms, bbox_params=A.BboxParams(
            format='yolo',
            label_fields=['class_labels'],
            min_visibility=0.3
        ))
    
    def augment_image(self, image_path, label_path, output_image_path, output_label_path):
        """
        Augment a single image and its labels.
        
        Args:
            image_path: Path to source image
            label_path: Path to source YOLO label file
            output_image_path: Path to save augmented image
            output_label_path: Path to save augmented labels
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Load labels
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
            
            # Apply augmentation
            transform = self.create_augmentation_pipeline()
            
            if len(bboxes) > 0:
                augmented = transform(image=image, bboxes=bboxes, class_labels=class_labels)
            else:
                # No bboxes, just augment image
                augmented = transform(image=image, bboxes=[], class_labels=[])
            
            # Save augmented image
            aug_image = cv2.cvtColor(augmented['image'], cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_image_path, aug_image)
            
            # Save augmented labels
            with open(output_label_path, 'w') as f:
                for bbox, class_id in zip(augmented['bboxes'], augmented['class_labels']):
                    cx, cy, w, h = bbox
                    # Ensure class_id is an integer
                    class_id = int(class_id)
                    f.write(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
            
            return True
            
        except Exception as e:
            print(f"Error augmenting {image_path}: {e}")
            return False
    
    def augment_dataset(self, images_dir, labels_dir, output_images_dir, output_labels_dir, progress_callback=None):
        """
        Augment entire dataset.
        
        Args:
            images_dir: Directory containing source images
            labels_dir: Directory containing source labels
            output_images_dir: Directory to save augmented images
            output_labels_dir: Directory to save augmented labels
            progress_callback: Optional callback function(current, total, message)
        
        Returns:
            Number of augmented images created
        """
        if not self.config.enabled:
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
            
            # Generate multiple augmentations per image
            for aug_idx in range(self.config.augmentations_per_image):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                base_name = os.path.splitext(img_file)[0]
                ext = os.path.splitext(img_file)[1]
                
                aug_img_name = f"aug_{aug_idx}_{timestamp}_{base_name}{ext}"
                aug_label_name = f"aug_{aug_idx}_{timestamp}_{base_name}.txt"
                
                aug_img_path = os.path.join(output_images_dir, aug_img_name)
                aug_label_path = os.path.join(output_labels_dir, aug_label_name)
                
                if self.augment_image(img_path, label_path, aug_img_path, aug_label_path):
                    augmented_count += 1
                
                if progress_callback:
                    current = idx * self.config.augmentations_per_image + aug_idx + 1
                    total = total_images * self.config.augmentations_per_image
                    progress_callback(current, total, f"Augmenting {img_file} ({aug_idx + 1}/{self.config.augmentations_per_image})")
        
        return augmented_count
    
    def preview_augmentation(self, image_path, label_path):
        """
        Generate a preview of augmentation without saving.
        
        Args:
            image_path: Path to source image
            label_path: Path to source YOLO label file
        
        Returns:
            Tuple of (augmented_image_array, augmented_bboxes, class_labels) or None
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Load labels
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
            
            # Apply augmentation
            transform = self.create_augmentation_pipeline()
            
            if len(bboxes) > 0:
                augmented = transform(image=image, bboxes=bboxes, class_labels=class_labels)
            else:
                augmented = transform(image=image, bboxes=[], class_labels=[])
            
            return (augmented['image'], augmented['bboxes'], augmented['class_labels'])
            
        except Exception as e:
            print(f"Error previewing augmentation: {e}")
            return None
