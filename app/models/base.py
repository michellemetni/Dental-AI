from abc import ABC, abstractmethod

class ModelStrategy(ABC):
    @abstractmethod
    def predict(self, image_path: str):
        """All models must implement this method"""
        pass