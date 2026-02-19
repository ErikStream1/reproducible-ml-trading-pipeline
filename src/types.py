from __future__ import annotations

from typing import TypeAlias, Sequence, Any
import numpy as np
import pandas as pd
from numpy.typing import NDArray

IntArray: TypeAlias = Sequence[int]

FloatArray: TypeAlias = NDArray[np.floating]
VectorArray: TypeAlias = NDArray[np.floating]
MatrixArray: TypeAlias = NDArray[np.floating]
IndexLike: TypeAlias = pd.Index

SeriesLike: TypeAlias = pd.Series
FrameLike: TypeAlias = pd.DataFrame
VectorLike: TypeAlias = Sequence[float] | FloatArray | SeriesLike

XLike: TypeAlias = FrameLike
YLike: TypeAlias =  VectorLike
Prediction: TypeAlias =  VectorLike

ConfigLike: TypeAlias = dict[str, Any]


