from __future__ import annotations
from src.types import ConfigLike
import numpy as np

def walk_forward_splits(n:int, cfg:ConfigLike):
    
    split_cfg = cfg["training"]["split"]

    train_size = split_cfg.get("train_size", 200)
    test_size = split_cfg.get("test_size", 50)

    if train_size <= 0:
        raise ValueError("Train size <= 0. Check training.yaml")
    
    if test_size <= 0:
        raise ValueError("Test size <= 0. Check training.yaml")
    
    step = split_cfg.get("step", test_size)

    if step <= 0:
        raise ValueError("Step <= 0. Check training.yaml")

    start = train_size
    
    while start + test_size <= n:
        train_idx = np.arange(0, start)
        test_idx = np.arange(start, start + test_size)
        
        yield train_idx, test_idx
        
        start += step