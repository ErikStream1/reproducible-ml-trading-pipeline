from src.config import load_config
from src.pipelines import (run_data_pipeline,
                           run_training_pipeline,
                           run_inference_pipeline,
                           run_model_validation_pipeline,
                           run_collect_quotes_pipeline,
                           run_realtime_simulation_step
                           )
from src.utils import setup_logging
import logging


def main():
    
    cfg = load_config(
        "configs/data.yaml",
        "configs/features.yaml",
        "configs/training.yaml",
        "configs/models.yaml",
        "configs/inference.yaml",
        "configs/strategy.yaml",
        "configs/execution.yaml",
        "configs/backtest.yaml",
        "configs/bitso.yaml",
        "configs/quotes.yaml",
        "configs/realtime_simulation.yaml",     
        "configs/logging.yaml"
    )

    log_cfg = cfg["logging"]
    level_name = str(log_cfg.get("level", "DEBUG")).upper()
    level = getattr(logging, level_name, logging.DEBUG)
    
    setup_logging(level=level,
                  log_file=log_cfg.get("file", None),
                  overwrite=log_cfg.get("overwrite", False),
                  )
    
    #run_data_pipeline(cfg)
    #run_model_validation(cfg)
    #run_training_pipeline(cfg)
    #run_inference_pipeline(cfg)
    run_collect_quotes_pipeline(cfg=cfg)
if __name__ == "__main__":
    main()