from __future__ import annotations

from typing import Self, final
from src.types import XLike, YLike, Prediction
from dataclasses import replace
from xgboost import XGBRegressor

from src.models import (BaseModel, 
                        ModelInfo, 
                        paramsLike, 
                        infoLike,
                        payloadLike,)

@final
class XGBoostModel(BaseModel):

    def __init__(
                self,
                info : infoLike | None = None,
                params : paramsLike = None,
                ):
        
        default_params = {
            "n_estimators" : 300,
            "learning_rate" : 0.05,
            "max_depth" : 4,
            "subsample" : 0.9,
            "colsample_bytree" : 0.9,
            "random_state" : 42,
        }
        self.params = {**default_params, **(params or {})}
        
        self.info = info or ModelInfo(name = "xgboost", params = self.params)
        super().__init__(info = self.info)
        self.model = XGBRegressor(n_estimators=self.params["n_estimators"],
                                  learning_rate=self.params["learning_rate"],
                                  max_depth=self.params["max_depth"],
                                  subsample=self.params["subsample"],
                                  colsample_bytree=self.params["colsample_bytree"],
                                  random_state=self.params["random_state"])
        
        

    def fit(self, X: XLike, y: YLike)-> Self:
        if self.info is not None:
            self.info = replace(self.info, feature_names = X.columns)
        
        self.model.fit(X,y)
        return self
    
    def predict(self, X:XLike) ->Prediction:
        return self.model.predict(X)
    
    def _get_serializable_model(self)-> XGBRegressor:
        return self.model
    
    @classmethod
    def from_payload(cls, payload: payloadLike)-> Self:
        """
        Reconstruct an XGBoostModel instance from a serialized payload.
        """
        
        info_dict = payload["info"]
        info = ModelInfo(**info_dict)
        params = info.params or {}
        
        obj = cls(params = params, info = info)
        obj.model = payload["model"]
        return obj