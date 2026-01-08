from app.core.augmentation.base import AugmentationEffect
import albumentations as A

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
