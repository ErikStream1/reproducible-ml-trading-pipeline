from __future__ import annotations

from typing import Any

from pathlib import Path
from src.data import BitsoConfig, BitsoError
from datetime import datetime, timezone
from decimal import Decimal
from src.models import paramsLike, payloadLike
from src.types import ConfigLike
import requests
from tenacity import (retry,
                      wait_exponential,
                      stop_after_attempt,
                      retry_if_exception_type
                      )

def _parse_dt_utc(dt_str:str)->datetime:
    s = dt_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

class BitsoClient:
    def __init__(self, cfg: ConfigLike):
        self.obj = BitsoConfig(
            base_url = cfg["base_url"],
            timeout_s = cfg["timeout_s"]
        ) if cfg else BitsoConfig()
        
        self._session = requests.Session()
        
    @retry(
        wait = wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop = stop_after_attempt(5),
        retry = retry_if_exception_type((requests.RequestException, BitsoError)),
        reraise = True
    )
    def _get(self, path: Path, params: paramsLike = None,)->dict[str, Any]:
        url = f"{self.obj.base_url}{path}"
        r = self._session.get(url, params = params, timeout=self.obj.timeout_s)
        r.raise_for_status
        data = r.json()
        if not data.get("success", False):
            raise BitsoError(f"Bitso API returned success = false: {data}")
        
        return data
    
    def list_available_books(self)->list[dict[str,Any]]:
        data = self._get(Path("/available_books/"))
        return data["payload"]
    
    def get_ticker(self, book:str)->payloadLike:
        data = self._get(Path("/ticker/"), params = {"book":book})
        return data["payload"]
    
    def get_best_bid_ask_from_ticker(self, book: str)->tuple[datetime, Decimal, Decimal]:
        p = self.get_ticker(book)
        ts = _parse_dt_utc(p["created_at"])
        bid = Decimal(str(p["bid"]))
        ask = Decimal(str(p["ask"]))
        return ts, bid, ask