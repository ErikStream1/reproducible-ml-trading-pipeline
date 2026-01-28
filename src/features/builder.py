from __future__ import annotations
from src.types import ConfigLike, FrameLike
import numpy as np

def build_features(df: FrameLike, cfg: ConfigLike) -> FrameLike:
    """
    Create financial features from Bitcoin price data.

    Features added:

    1. Return
       - Definition: Daily percentage change in closing price.
       - Indicates: Gain or loss relative to the previous day.

    2. LogReturn
       - Definition: Daily log return of the closing price.
       - Indicates: Normalized returns for statistical stability.

    3. MA_n
       - Definition: n-day moving average of closing price.
       - Indicates: Short-term trend direction.

    4. Volatility_n
       - Definition: Rolling n-day standard deviation of daily returns.
       - Indicates: Short-term price fluctuation / risk.

    5. Momentum_n
       - Definition: Difference between today's closing price and closing price n days ago.
       - Indicates: Strength and direction of price movement.

    Notes:
    - Some features (e.g., moving averages, volatility, momentum) will contain NaN
      for the first N rows where calculation is not possible.
    - Do not drop NaNs here; handle them later in the training pipeline.
    """
    df = df.copy()
    features_cfg = cfg["features"]

    base = features_cfg.get("base_column", "Close")
    
    # Returns
    returns_cfg = features_cfg.get("returns", {})
    pct_cfg = returns_cfg.get("pct_change", {})
    
    if pct_cfg.get("enabled", False):
       periods = pct_cfg.get("periods", [1])
       output_names = pct_cfg.get("output_names")
       name_prefix = pct_cfg.get("name_prefix", "Return")
       for p in periods:
         name = output_names.get(str(p)) if isinstance(output_names, dict) else None
         if not name:
            name = f"{name_prefix}_{p}"
         df[name] = df[base].pct_change(periods = int(p))
       
    log_cfg = returns_cfg.get("log_diff",{})
    if log_cfg.get("enabled", False):
       name = log_cfg.get("name", "LogReturn")
       df[name] = np.log(df[base]).diff()
   
   #Moving Average
    ma_cfg = returns_cfg.get("moving_average", {})
    if ma_cfg.get("enabled", False):
       windows_ma = ma_cfg.get("windows", [7])
       output_names = ma_cfg.get("output_names")
       name_prefix = ma_cfg.get("name_prefix", "MA")
       for wma in windows_ma:
          name = output_names.get(str(wma)) if isinstance(output_names, dict) else None
          if not name:
             name = f"{name_prefix}_{wma}"
          
          df[name] = df[base].rolling(window = wma).mean()
    
    #Volatility      
    volatility_cfg = returns_cfg.get("volatility",{})
    if volatility_cfg.get("enabled", False):
       windows_volatility = volatility_cfg.get("windows", [7])
       on_col = volatility_cfg.get("on", "Return_1")
       output_names = volatility_cfg.get("output_names")
       name_prefix = volatility_cfg.get("name_prefix", "Volatility_7")
       for wv in windows_volatility:
          name = output_names.get(str(wv)) if isinstance(output_names, dict) else None
          if not name:
             name = f"{name_prefix}_{wv}"
          df[name] = df[on_col].rolling(wv).std()
          
    #Momentum       
    momentum_cfg = returns_cfg.get("momentum", {})
    if momentum_cfg.get("enabled", False):
       lags = momentum_cfg.get("lags", [7])
       name_prefix = momentum_cfg.get("name_prefix", "Momentum_7")
       output_names = momentum_cfg.get("output_names")
       for lag in lags:
         name = output_names.get(str(lag)) if isinstance(output_names, dict) else None
         
         if not name:
            name = f"{name_prefix}_{lag}"
         df[name] = df[base] - df[base].shift(lag)
      
    return df  