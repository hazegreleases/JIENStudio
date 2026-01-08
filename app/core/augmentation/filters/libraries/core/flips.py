from app.core.augmentation.base import AugmentationEffect
import albumentations as A

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
