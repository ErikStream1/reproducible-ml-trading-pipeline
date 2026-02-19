from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator
import logging
import time

@contextmanager
def log_step(logger: logging.Logger, step: str, level:int = logging.INFO)->Iterator[None]:
    
    start = time.perf_counter()
    logger.info("Running %s", step)
    
    try:
        yield
    except Exception:
        logger.exception("FAILED %s", step)
        raise
    
    else:
        elapsed = time.perf_counter() - start
        logger.log(level, "Done %s (%.2fs)", step, elapsed)

def log_drop(
    logger:logging.Logger, 
    name: str,
    before: int,
    after: int,
    level: int = logging.INFO
    )->None:
    
    dropped = before - after
    if dropped > 0:
        logger.log(
                   level, 
                   "%s dropped: before = %d after = %d dropped = %d", 
                    name, before, after, dropped
                    )
    else:
        level = logging.DEBUG
        logger.log(level, "No rows were dropped.")
    
