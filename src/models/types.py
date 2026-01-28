from __future__ import annotations
from typing import Any, Protocol, Mapping, TypeVar, TypeAlias
from dataclasses import dataclass

from src.types import XLike, YLike, Prediction, PathLike, IndexLike

paramsLike: TypeAlias = Mapping[str, Any] | None
payloadLike: TypeAlias = dict[str, Any]
######################################################################

@dataclass(frozen = True)
class ModelInfo:
    version: str = "0.1"
    name: str = ""
    feature_names: IndexLike | None = None
    params: paramsLike = None
    target_name: str = "LogReturn"

infoLike: TypeAlias = ModelInfo
    
######################################################################

class ModelLike(Protocol):
    def fit(self, X: XLike, y: YLike)->"ModelLike":...
    def predict(self, X:XLike) -> Prediction:...
    def save(self, path:PathLike)->None:...
######################################################################

T = TypeVar("T", bound="SerializableModelLike")

class SerializableModelLike(ModelLike, Protocol):
    @classmethod
    def from_payload(cls: type[T], payload: Mapping[str, Any])->T: ...
    def save(self, path: PathLike)->None: ...

######################################################################
