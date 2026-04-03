from __future__ import annotations

import requests
import time
import hashlib
import hmac
import json
from src.execution import BitsoOrderResponse, BitsoBrokerError
from src.types import ConfigLike, payloadLike
from typing import Any

class BitsoBrokerClient:
    
    def __init__(self, cfg: ConfigLike):
        live_cfg = cfg["live_broker"]
        local_cfg = cfg["local_live_broker"] #Do not store API keys or secrets in the repository. 
                                             #Keep them in a local .env or .yaml file that is ignored by Git.
        self.base_url = (live_cfg.get("base_url", "https://api.bitso.com/v3")).rstrip("/")
        self.timeout_s = float(live_cfg.get("timeout_s", 10))
        self.api_key = str(local_cfg["api_key"])
        self.api_secret = str(local_cfg["api_secret"])
        self.session = requests.Session()
        
    def _build_auth_headers(self, method: str, request_path:str, payload_str: str)->dict[str, Any]:
        nonce = str(int(time.time() * 1_000_000))
        message = f"{nonce}{method.upper()}{request_path}{payload_str}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return {"Authorization": f"Bitso {self.api_key}:{nonce}:{signature}"}


    def _private_request(
        self,
        method: str,
        request_path: str,
        payload_obj: payloadLike,
    ) -> dict[str, Any]:
        payload = json.dumps(payload_obj, separators=(",", ":"), sort_keys=True)
        headers = {
            "Content-Type": "application/json",
            **self._build_auth_headers(method=method, request_path=request_path, payload_str=payload),
        }

        response = self.session.request(
            method=method.upper(),
            url=f"{self.base_url}{request_path}",
            data=payload,
            headers=headers,
            timeout=self.timeout_s,
        )
        response.raise_for_status()
        body = response.json()
        if not body.get("success", False):
            raise BitsoBrokerError(f"Bitso private API rejected request: {body}")

        return body

    def place_market_order(self, *, book: str, side: str, major: float) -> BitsoOrderResponse:
        body = self._private_request(
            method="POST",
            request_path="/orders/",
            payload_obj={
                "book": book,
                "side": side,
                "type": "market",
                "major": str(major),
            },
        )
        payload = body.get("payload", {})
        return BitsoOrderResponse(
            oid=payload.get("oid"),
            status="submitted",
            raw=body,
        )