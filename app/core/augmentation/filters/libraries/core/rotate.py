from app.core.augmentation.base import AugmentationEffect
import albumentations as A
import cv2

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
