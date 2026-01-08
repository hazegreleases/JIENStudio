from app.core.augmentation.base import AugmentationEffect
import albumentations as A

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
