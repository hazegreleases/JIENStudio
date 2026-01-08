from app.core.augmentation.base import AugmentationEffect
import albumentations as A

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
