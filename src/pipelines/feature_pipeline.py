from __future__ import annotations

from src.features import build_features
from src.types import ConfigLike, FrameLike

def run_feature_pipeline(df: FrameLike,
                         cfg:ConfigLike)->FrameLike:
    
    path = cfg["data"]["paths"].get("features_path", None)
    feature_cfg = cfg["features"]
    
    drop_columns = feature_cfg.get("drop_columns", ["Date","Return_1"])
        
    df = build_features(df, cfg)
    
    target = cfg["data"]["schema"].get("target_column")
    horizon = int(feature_cfg.get("target_horizon", 1))
    
    if target in df.columns and horizon > 0:
        df[target] = df[target].shift(-horizon)
        
    df = df.drop(columns=drop_columns)
    
    if path is not None:
        df.to_csv(path, index = False)
    
    return df