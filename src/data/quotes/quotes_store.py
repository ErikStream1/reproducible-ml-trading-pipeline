from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from src.data import QuoteSnapshot

import pandas as pd

def to_utc(dt: datetime)->datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

class QuoteStore:
    """Store snapshots in parquet files"""
    
    def __init__(self, out_dir: Path)->None:
        self.out_dir = out_dir
        
    def write_chunk(self, rows: list[QuoteSnapshot])->Path:
        if not rows:
            raise ValueError("No rows to write")
        
        book = rows[0].book
        date_str = to_utc(rows[0].ts_exchange).date().isoformat()
        
        part_dir = self.out_dir/ f"book={book}" / f"date={date_str}"
        part_dir.mkdir(parents = True, exist_ok = True)
        
        now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        fname = f"quotes_{now}_{len(rows)}.parquet"
        out_path = part_dir / fname
        
        data: list[dict] = []
        
        for r in rows:   
            data.append({
                "ts_exchange": to_utc(r.ts_exchange),
                    "book": r.book,
                    "ask": float(r.ask),
                    "bid": float(r.bid),
                    "mid": (r.ask+r.bid)/2,
                    "source": r.source, 
            })
        
        df = pd.DataFrame.from_records(data, index = (range(len(rows))))
            
        df.sort_values("ts_exchange").reset_index(drop = True)
        df.to_parquet(out_path, index = False)
        
        return out_path