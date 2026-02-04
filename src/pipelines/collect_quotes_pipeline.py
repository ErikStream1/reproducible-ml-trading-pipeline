from __future__ import annotations

import logging

from src.data import (collect_quotes,
                      BitsoClient)

from src.types import ConfigLike

logger = logging.getLogger(__name__)

def run_collect_quotes_pipeline(cfg: ConfigLike)->None:
    quotes_cfg = cfg["quotes"]
    client_cfg = cfg["client"]
    
    client = BitsoClient(client_cfg)
    books = client.list_available_books()
    available = {b["book"] for b in books if "book" in b}
    book = quotes_cfg["book"]
    if book not in available:
        logger.warning("Book %s is not in available books", book)
        logger.info("Some available books: ", sorted(list(available))[:30])
        logger.info("Look for the correct book and update configs/quotes.yaml")

    collect_quotes(cfg=cfg)
    
    