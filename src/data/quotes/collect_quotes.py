from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from src.data import (BitsoClient,
                      QuoteSnapshot,
                      QuoteStore)

from src.types import ConfigLike

logger = logging.getLogger(__name__)


def _collect_ticker_rest(cfg:ConfigLike, client:BitsoClient, store:QuoteStore)->None:
    quotes_cfg = cfg["quotes"]
    book = quotes_cfg["book"]
    flush_every_n = quotes_cfg.get("flush_every_n", 200)
    poll_interval_s = quotes_cfg.get("poll_interval_s", 2.0)
    
    buffer: list[QuoteSnapshot] = []
    logger.debug("Starting ticker_rest collector for book= %s", book)
    
    while True:
        ts_local = datetime.now(timezone.utc)
        ts_ex, bid, ask = client.get_best_bid_ask_from_ticker(book)
        buffer.append(QuoteSnapshot(
            ts_exchange=ts_ex,
            ts_local=ts_local,
            book = book,
            ask = float(ask),
            bid = float(bid),
            source="ticker_rest"
        ))
        
        if len(buffer) >= flush_every_n:
            out_path = store.write_chunk(buffer)
            logger.debug("Wrote %d quotes -> %s", len(buffer), out_path)
        
        time.sleep(poll_interval_s)
            
def collect_quotes(cfg: ConfigLike):
    quotes_cfg = cfg["quotes"]
    client_cfg = cfg["client"]
    
    store = QuoteStore(out_dir = quotes_cfg["out_dir"] or "data/quotes")
    client = BitsoClient(cfg = client_cfg or None)
    
    if quotes_cfg["mode"] == "ticker_rest":
        _collect_ticker_rest(cfg = cfg, 
                             client = client, 
                             store = store)
 