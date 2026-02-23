from __future__ import annotations

from pathlib import Path

from src.data import load_historic_btc_data, load_btc_data_daily_candles, validate_btc_data
from src.types import ConfigLike,FrameLike

import pandas as pd

RAW_PATH = "data/raw/"
PROCESSED_PATH = "data/processed/processed_btc_usd.csv"

def run_data_pipeline(cfg:ConfigLike, 
                      tmp_output_path = PROCESSED_PATH
                      )->FrameLike:
        
    data_cfg = cfg["data"]
    paths = data_cfg["paths"]

    raw_dir = Path(paths.get("raw_dir", RAW_PATH))
    raw_dir.mkdir(parents=True, exist_ok=True)

    market_data = data_cfg["market_data"]
    symbol = market_data["Symbol"].get("BTC", "BTC-USD")
    interval = market_data["interval"]

    base_dir = raw_dir / f"candles_{interval}" / f"symbol={symbol}"
    base_dir.mkdir(parents=True, exist_ok=True)

    raw_data_path = base_dir / "historic_candles.csv"

    if raw_data_path.exists():
        df_old = pd.read_csv(raw_data_path)
        daily_candle = load_btc_data_daily_candles(ticker=symbol)
        df = pd.concat([df_old, daily_candle], ignore_index=True)
    else:
        df = load_historic_btc_data()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")
    df = df.drop_duplicates(subset=["Date"], keep="last").reset_index(drop=True)
    
    validate_btc_data(df)
    df.to_csv(raw_data_path, index=False)

    return df
