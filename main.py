
import logging
from src.config import load_config
from src.pipelines.data_pipeline import run_data_pipeline
from src.pipelines.training_pipeline import run_training_pipeline
from src.pipelines.inference_pipeline import run_inference_pipeline
from src.pipelines.validation_pipeline import run_model_validation_pipeline
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
        "configs/backtest.yaml"
    )
    
    #run_data_pipeline(cfg)
    #run_model_validation(cfg)
    #run_training_pipeline(cfg)
    run_inference_pipeline(cfg)
if __name__ == "__main__":
    main()