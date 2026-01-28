from __future__ import annotations
from src.types import ConfigLike
from src.models import ModelLike, LinearModel, XGBoostModel

def build_model(cfg : ConfigLike) -> ModelLike:
    model_cfg = cfg["models"]
    active_model = cfg["training"]["model_run"].get("active_model", "xgboost_v1")

    act_model = model_cfg[active_model]
    model_type = act_model["type"]
    params = act_model.get("params", {})
    model = ""
    if model_type == "linear_regression":
        model = LinearModel(alpha = params)
    
    elif model_type == "xgboost":
        model = XGBoostModel(params = params)
    
    elif model == "":
        raise ValueError(f"Model {model_type} not found.")
    
    return model