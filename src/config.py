from __future__ import annotations
from typing import Any

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

def deep_merge(
                a: dict[str, Any],
                b: dict[str, Any]
            ) -> dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if (
            k in out
            and isinstance(out[k], dict)
            and isinstance(v, dict)
        ): 
            out[k] = deep_merge(out[k], v)
        
        else:
            out[k] = v
    
    return out

def load_config(*paths: str|Path) -> dict[str, Any]:
    cfg: dict[str, Any] = {}
    for p in paths:
        cfg = deep_merge(cfg, load_yaml(p))
    return cfg