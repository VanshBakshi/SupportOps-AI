import sys
from loguru import logger

_configured = False

def setup_logging():
    global _configured
    if _configured:
        return
    logger.remove()
    logger.add(sys.stderr, level="INFO", enqueue=True)
    logger.add("logs/supportops.log", rotation="10 MB", retention="14 days", compression="zip", enqueue=True)
    _configured = True

__all__ = ["logger", "setup_logging"]
