import logging
from src.utils.logger import setup_logging 

def test_setup_logging_persists_logs(tmp_path) -> None:
    

    log_path = tmp_path / "logs" / "pipeline.log"
    setup_logging(level=logging.INFO, log_file=str(log_path))

    logger = logging.getLogger("tests.logger")
    logger.info("persist me")

    logging.shutdown()

    assert log_path.exists()
    assert "persist me" in log_path.read_text(encoding="utf-8")
