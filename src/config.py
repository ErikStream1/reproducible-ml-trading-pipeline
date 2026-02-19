from __future__ import annotations
from typing import Any
from src.utils import deep_merge
from pathlib import Path
import yaml


def load_yaml(path:str|Path) -> dict[str, Any]: 
    path = Path(path)
    if not path.exists():
        raise FileExistsError(f"Config file not found: {path}")
    
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a dict. Got {type(data) in {path}}")
    
    return data

def load_config(*paths: str|Path) -> dict[str, Any]:
    cfg: dict[str, Any] = {}
    for p in paths:
        cfg = deep_merge(cfg, load_yaml(p))
    return cfg