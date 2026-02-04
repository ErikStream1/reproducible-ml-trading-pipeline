
import logging
from src.config import load_config
from src.pipelines import (run_data_pipeline,
                           run_training_pipeline,
                           run_inference_pipeline,
                           run_model_validation_pipeline,
                           run_collect_quotes_pipeline)
from src.utils.logger import setup_logging



def main():
    setup_logging(logging.DEBUG)
    
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
        "configs/quotes.yaml"
    )
    
    #run_data_pipeline(cfg)
    #run_model_validation(cfg)
    #run_training_pipeline(cfg)
    #run_inference_pipeline(cfg)
    run_collect_quotes_pipeline(cfg=cfg)
if __name__ == "__main__":
    main()