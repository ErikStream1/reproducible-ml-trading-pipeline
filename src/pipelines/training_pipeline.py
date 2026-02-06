from __future__ import annotations
from pathlib import Path
from src.models import ModelLike
from src.types import ConfigLike, PathLike

from src.utils import log_step
from src.models import build_model

from src.pipelines import run_feature_pipeline, run_data_pipeline

import logging

logger = logging.getLogger(__name__)

def run_training_pipeline(
    cfg : ConfigLike
)->tuple[PathLike, ModelLike]:
    
    target = cfg["data"]["schema"].get("target_column", "LogReturn")
    
    with log_step(logger, "Data pipeline"):
        df = run_data_pipeline(cfg)
    
    with log_step(logger, "Features"):        
        df = run_feature_pipeline(df, cfg)
    
    df = df.dropna().reset_index(drop = True)
    
    training_cfg = cfg["training"]

    X = df.drop(columns=target)
    y = df[target]
    
    with log_step(logger, "Build model"):
        model = build_model(cfg)

    model_name = model.__getattribute__("info").name
    
    with log_step(logger, "Fit model"):
        model.fit(X, y)

    artifacts_cfg = training_cfg["artifacts"]
    output_dir = Path(artifacts_cfg["model_output_dir"])
    output_dir.mkdir(parents = True, exist_ok=True)
    
    filename = artifacts_cfg["model_filenames"][model_name]
    complete_path:PathLike = output_dir / filename
    
    with log_step(logger, "Save model"):
        model.save(complete_path)
    
    logger.info("%s model saved at %s", model_name, complete_path)
    
    return complete_path, model

