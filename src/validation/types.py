from __future__ import annotations
from typing import TypeAlias, Any, Iterable
from src.types import SummaryLike

GapSummaryLike: TypeAlias = SummaryLike
FoldMetricLike: TypeAlias = list[dict[str,float]]
FoldLike: TypeAlias = Iterable[dict[str, Any]]

