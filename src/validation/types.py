from __future__ import annotations
from typing import TypeAlias, Any, Iterable

SummaryLike: TypeAlias = dict[str, Any]
GapSummaryLike: TypeAlias = dict[str, float]
FoldMetricLike: TypeAlias = list[dict[str,float]]
FoldLike: TypeAlias = Iterable[dict[str, Any]]