from __future__ import annotations

from src.types import ConfigLike
from src.pipelines import run_data_pipeline, run_feature_pipeline
from src.validation import wfs_cross_validation, summarize

def run_model_validation_pipeline (cfg:ConfigLike)->None:
  
    df = run_data_pipeline(cfg)

    df = run_feature_pipeline(df, cfg)
    df = df.dropna().reset_index(drop = True)
    
    cv_iter = wfs_cross_validation(df, cfg)
    summary = summarize(fold_outputs=cv_iter,)
    
    print(summary)
    