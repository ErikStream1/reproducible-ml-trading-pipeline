from __future__ import annotations

from typing import Self
from src.types import XLike, YLike, Prediction, PathLike
from src.models import infoLike, payloadLike
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import asdict


import joblib
    
class BaseModel(ABC):
    """
    Abstract base class for all predictive models in the project.
    
    This class defines a common interface to ensure that all models
    can be trained, used for inference, and serialized in a consistent way.
    """
    def __init__(self, info: infoLike):
        self.info = info
     
    @abstractmethod   
    def fit(self, X:XLike, y:YLike) -> Self:
        ...
        
    @abstractmethod
    def predict(self, X:XLike)->Prediction:
        ...
    
    def save(self, path: PathLike) -> None:
        """
        Persist the trained model and its metadata to disk.
        """
        if self.info is None:
            raise ValueError(f"There is no info to save in the model {self.info}.")
        
        if path is None:
            raise ValueError("Save path not found.")
        
        save_path = Path(path)
        save_path.parent.mkdir(parents = True, exist_ok=True)
        
        payload = {
            "model" : self._get_serializable_model(),
            "info" : asdict(self.info)
        }
        
        joblib.dump(payload, path)
    
    @classmethod
    def load(cls, path: PathLike) -> Self:
        """
        Load a previously saved model from disk.
        """
        payload = joblib.load(path)
        
        return cls.from_payload(payload)
    
    @classmethod
    @abstractmethod
    def from_payload(cls, payload: payloadLike) -> Self:
        """
        Reconstruct a model instance from a serialized payload.
        """
        ...
    
    @abstractmethod
    def  _get_serializable_model(self):
        """
        Return the internal trained model object that can be serialized.
    
        This is typically a scikit.learn or XGBoost model instance.
        """
        ...