from __future__ import annotations

import logging
import time
from pathlib import Path
from src.data import (BitsoClient,
                      QuoteSnapshot,
                      QuoteStore,
                      CollectQuotesConfig)

from src.types import ConfigLike

logger = logging.getLogger(__name__)


def _collect_ticker_rest(cqc_obj:CollectQuotesConfig, client:BitsoClient, store:QuoteStore)->None:

    book = cqc_obj.book
    flush_every_n = cqc_obj.flush_every_n
    poll_interval_s = cqc_obj.poll_interval_s
    
    buffer: list[QuoteSnapshot] = []
    logger.debug("Starting ticker_rest collector for book= %s", book)
    
    while True:
        ts_ex, bid, ask = client.get_best_bid_ask_from_ticker(book)
        buffer.append(QuoteSnapshot(
            ts_exchange=ts_ex,
            book = book,
            ask = float(ask),
            bid = float(bid),
            source="ticker_rest"
        ))
        
        if len(buffer) >= flush_every_n:
            out_path = store.write_chunk(buffer)
            logger.debug("Wrote %d quotes -> %s", len(buffer), out_path)
            buffer.clear()
            
        time.sleep(poll_interval_s)
            
def collect_quotes(cfg: ConfigLike):
    quotes_cfg = cfg["quotes"]
    client_cfg = cfg["client"]
    
    book = quotes_cfg["book"]
    mode = quotes_cfg["mode"]
    poll_interval_s = quotes_cfg["poll_interval_s"]
    flush_every_n = quotes_cfg["flush_every_n"]
    out_dir = quotes_cfg["out_dir"]
    
    c = CollectQuotesConfig(
        book = book,
        mode = mode,
        poll_interval_s=poll_interval_s,
        flush_every_n=flush_every_n,
        out_dir=out_dir
        )
    
    store = QuoteStore(out_dir = quotes_cfg["out_dir"] or Path("data/quotes"))
    client = BitsoClient(cfg = client_cfg)
    
    if quotes_cfg["mode"] == "ticker_rest":
        _collect_ticker_rest(cqc_obj = c, 
                             client = client, 
                             store = store)
        return