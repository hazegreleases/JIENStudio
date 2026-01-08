from app.core.augmentation.base import AugmentationEffect
import albumentations as A

class RandomCropEffect(AugmentationEffect):
    def __init__(self, height_fraction=0.8, width_fraction=0.8, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.height_fraction = height_fraction
        self.width_fraction = width_fraction

    def get_transform(self):
        target_h = int(640 * self.height_fraction)
        target_w = int(640 * self.width_fraction)
        
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
