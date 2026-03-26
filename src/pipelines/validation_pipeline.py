from __future__ import annotations

from src.types import ConfigLike, SummaryLike, FrameLike
from src.validation import wfs_cross_validation, summarize

def run_model_validation_pipeline(df: FrameLike, cfg:ConfigLike)->SummaryLike:

    cv_iter = wfs_cross_validation(df, cfg)
    summary = summarize(fold_outputs=cv_iter,)
    
    return summary
    