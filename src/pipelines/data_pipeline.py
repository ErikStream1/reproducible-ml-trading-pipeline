from __future__ import annotations

from src.data import load_btc_data, validate_btc_data
from src.types import ConfigLike,FrameLike
import os
import pandas as pd

RAW_PATH = "data/raw/btc_usd.csv"
PROCESSED_PATH = "data/processed/processed_btc_usd.csv"
COL_NAMES = ["Date","Open", "High", "Low", "Close", "Volume"]

def run_data_pipeline(cfg:ConfigLike, 
                      tmp_output_path = PROCESSED_PATH
                      )->FrameLike:
    
    data_cfg = cfg["data"]
    
    paths = data_cfg["paths"]
    
    force_update = data_cfg["update"].get("enabled", False)
        
    raw_path = paths.get("raw_path", RAW_PATH)
    processed_path = paths.get("processed_path", tmp_output_path)
    
    if os.path.exists(raw_path) and not force_update:
        df = pd.read_csv(raw_path)
        
    else:
        df = load_btc_data()
        df.columns = COL_NAMES
        df.to_csv(raw_path, index = False)
        
    validate_btc_data(df)
    
    df.to_csv(processed_path, index = False)
    
    return df
