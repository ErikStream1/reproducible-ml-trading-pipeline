from __future__ import annotations
from pathlib import Path

from src.types import Prediction, ConfigLike, PathLike

from src.models import LinearModel, XGBoostModel
from src.pipelines import run_data_pipeline, run_feature_pipeline


def _load_model(model_path: PathLike) ->LinearModel|XGBoostModel:
    """
    Loads a trained model artifact.
    """ 
    
    model_path = str(model_path)
    
    if "linear" in model_path:
        return LinearModel.load(model_path) 

    elif "xgboost" in model_path:
        return XGBoostModel.load(model_path)
    
    else:
        raise ValueError("Model not found.")

def run_inference_pipeline(
    cfg: ConfigLike,
    model_path: PathLike = None
) -> Prediction:
    """
    End-to-end inference:
      1) Load + validate raw data (via data_pipeline)
      2) Build features (via feature_pipeline)
      3) Align columns to training feature set if available
      4) Predict and optionally save predictions
    """
    
    
    paths_cfg = cfg["data"]["paths"]
    
    raw_path = paths_cfg["raw_path"]
    processed_path = paths_cfg["processed_path"]
    
    
    if processed_path is not None:
        p = Path(processed_path).resolve()
        if "data/processed" in str(p):
            raise ValueError(
                "Inference pipeline is not allowed to write into data/processed."
                "Use processed_data_path = None or an artifacts/tmp path."
            )

    if processed_path is None:
        
        tmp_out = Path(raw_path).with_suffix(".processed_tmp.csv")
        df = run_data_pipeline(cfg, tmp_output_path=str(tmp_out))
        
        try:
            tmp_out.unlink(missing_ok=True)
        except Exception:
            pass
    else:
        df = run_data_pipeline(cfg)


    if model_path is None:
        inference_cfg = cfg["inference"]
        model_artifact_path = inference_cfg["artifacts"]["model_path"]
    else:
        model_artifact_path = model_path
        
    model = _load_model(model_artifact_path)
    df = run_feature_pipeline(df, cfg)
    
    df = df.dropna().reset_index(drop=True)
    
    X = df.drop(columns=cfg["data"]["schema"].get("target_column", "Close"), errors="ignore")
    
    feature_names = None
    if hasattr(model, "info") and getattr(model, "info") is not None:
        feature_names = getattr(model.info, "feature_names", None)
    
    if feature_names is not None and not feature_names.empty:
        for c in feature_names:
            if c not in X.columns:
                raise ValueError(f"Inference is missing required feature columns: {c}")

    
    X_next = X.tail(1)

    preds = model.predict(X_next)

    return preds
