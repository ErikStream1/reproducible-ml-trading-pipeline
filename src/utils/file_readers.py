import pandas as pd
from pathlib import Path

from src.types import FrameLike

def read_csv(file: Path)->FrameLike:
    return pd.read_csv(file)

def read_parquet(file: Path)->FrameLike:
    return pd.read_parquet(file)

def read(file: Path)->FrameLike | None:
    """
    Support csv and parquet
    """
    suffix = file.suffix
    if suffix == ".csv":
        return read_csv(file)
    elif suffix == ".parquet":
        return read_parquet(file)
    else:
        print("Unsupported extension")
        return