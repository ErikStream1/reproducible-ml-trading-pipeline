from __future__ import annotations
from dataclasses import replace
from typing import Any, Self, final
from src.types import XLike, YLike, Prediction
from sklearn.linear_model import Ridge
from src.models import BaseModel, ModelInfo, infoLike

@final
class LinearModel(BaseModel):
    """
    Linear Regression model using Ridge regularization.
    """
    
    def __init__(
                self, 
                alpha: float = 1.0, 
                info: infoLike | None = None
                ):
        
        """
        Initialize the linear regression model.
        
        Parameters
        ----------
        alpha = float
            Regularization strength for Ridge regression.
        info : ModelInfo | None
            Optional metadata describing the model.
        """
        
        self.info = info or ModelInfo(name = "linear_ridge", params = {"alpha": alpha})
        super().__init__(info = self.info)
        self.model = Ridge(alpha = alpha)
        
    def fit(self, X:XLike, y:YLike) -> Self:
        if self.info is not None:
            self.info = replace(self.info, feature_names = X.columns)
        self.model.fit(X,y)
        return self
    
    def predict(self, X:XLike) -> Prediction:
        return self.model.predict(X)
    
    def _get_serializable_model(self)-> Ridge:
        return self.model
    
    @classmethod
    def from_payload(cls, payload: dict[str, Any])-> Self:
        """Reconstruct a LinearModel instance from a serialized payload."""
        
        info_dict = payload["info"]
        info = ModelInfo(**info_dict)
        alpha = (info.params or {}).get("alpha", 1.0)
        
        obj = cls(alpha = alpha, info = info)
        obj.model = payload["model"]
        
        return obj