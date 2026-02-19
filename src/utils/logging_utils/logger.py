from pathlib import Path
import logging

def setup_logging(
    level: int=logging.INFO,
    log_file: str|None = None,
    overwrite: bool = False
)->None:
    
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents = True, exist_ok = True)
        mode = "w" if overwrite else "a"
        handlers.append(logging.FileHandler(log_path, mode = mode, encoding = "utf-8"))
    
    logging.basicConfig(
            level = level,
            format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt = "%Y-%m-%d %H:%M:%S",
            handlers=handlers,
            force = True
        )