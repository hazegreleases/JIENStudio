from abc import ABC, abstractmethod

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
        # Typically handled by factory, but could be useful
        pass
