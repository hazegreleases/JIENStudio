from app.core.augmentation.base import AugmentationEffect
import albumentations as A
import numpy as np

def damp_highlights(image, threshold=240, reduce_by=20, **kwargs):
    """
    Custom function to find pixels > threshold and subtract a value.
    """
    # Create a copy to avoid modifying the original directly if needed
    img = image.copy()
    
    # Create a mask where pixels are super bright
    # We check if ALL channels (R, G, B) are above threshold (white)
    # OR you could check if ANY channel is blown out. 
    # Let's use np.all for "Pure White" glare.
    mask = np.all(img >= threshold, axis=-1)
    
    # Subtract the value only where the mask is True
    # We use np.maximum to ensure we don't go below 0 (though unlikely here)
    # We need to cast to int to do math, then back to uint8
    img[mask] = np.clip(img[mask].astype(int) - reduce_by, 0, 255).astype(np.uint8)
    
    return img

class GlareDampener(AugmentationEffect):
    def __init__(self, threshold=240, reduce_by=20, probability=1.0, enabled=True):
        # Probability 1.0 because if you want this fix, you usually want it 
        # on every image that has glare. But for training variety, 0.5 is good.
        super().__init__(probability, enabled)
        self.threshold = threshold
        self.reduce_by = reduce_by

    def get_transform(self):
        # We use A.Lambda to wrap our custom numpy function
        return A.Lambda(
            image=lambda image, **kwargs: damp_highlights(
                image, 
                threshold=self.threshold, 
                reduce_by=self.reduce_by
            ),
            p=self.probability
        )

    def get_params(self):
        return {
            'threshold': self.threshold,
            'reduce_by': self.reduce_by
        }

    def set_params(self, params):
        if 'threshold' in params: 
            self.threshold = int(params['threshold'])
        if 'reduce_by' in params: 
            self.reduce_by = int(params['reduce_by'])