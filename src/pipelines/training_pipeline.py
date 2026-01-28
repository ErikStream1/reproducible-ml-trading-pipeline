from __future__ import annotations
from pathlib import Path
from src.models.types import ModelLike
from src.types import ConfigLike, PathLike

from src.models import build_model
from src.pipelines import run_feature_pipeline, run_data_pipeline 

import logging

logger = logging.getLogger(__name__)

def run_training_pipeline(
    cfg : ConfigLike
)->tuple[PathLike, ModelLike]:
    target = cfg["data"]["schema"].get("target_column", "LogReturn")
    
    current_fn = "Data pipeline"
    try:        
        logger.info("Running %s", current_fn)    
        df = run_data_pipeline(cfg)
        
        current_fn = "Features"
        logger.info("Running %s", current_fn)    
        df = run_feature_pipeline(df, cfg)
        
  
        
        df = df.dropna().reset_index(drop = True)
        
        training_cfg = cfg["training"]

        X = df.drop(columns=target)
        y = df[target]
        
        
        current_fn = "Build Model"
        logger.info("Running %s", current_fn)    
        model = build_model(cfg)

        model_name = model.__getattribute__("info").name
        
        current_fn = "Fit Model"
        logger.info("Running %s", current_fn)    
        model.fit(X, y)

        artifacts_cfg = training_cfg["artifacts"]
        output_dir = Path(artifacts_cfg["model_output_dir"])
        output_dir.mkdir(parents = True, exist_ok=True)
        
        filename = artifacts_cfg["model_filenames"][model_name]
        complete_path:PathLike = output_dir / filename
        
        current_fn = "Save Model"
        logger.info("Running %s", current_fn)    
        model.save(complete_path)
        
        logger.info(f"{model_name} Model saved at {complete_path}")
        
        return complete_path, model
    
    except:
        logger.exception(f"{current_fn} failed")
        raise
    
    