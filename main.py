
from src.config import load_config
from src.pipelines.data_pipeline import run_data_pipeline
from src.pipelines.training_pipeline import run_training_pipeline
from src.pipelines.inference_pipeline import run_inference_pipeline
from src.pipelines.validation_pipeline import run_model_validation_pipeline
from src.utils.logger import setup_logging
# run_data_pipeline("data/raw/btc_usd.csv", "data/processed/processed_btc_usd.csv", True) update data
# run_training_pipeline(raw_data_path="data/raw/btc_usd.csv",processed_data_path="data/processed/processed_btc_usd.csv") para reentrenar

def main():
    setup_logging()
    
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
    run_training_pipeline(cfg)
    #print(run_inference_pipeline(cfg))
if __name__ == "__main__":
    main()