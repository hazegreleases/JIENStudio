from app.core.augmentation.base import AugmentationEffect
import albumentations as A

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
