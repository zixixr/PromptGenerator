import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging():
    """Configure structured JSON logging."""
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )

    # Configure root logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Set specific log levels
    logging.getLogger("src").setLevel(logging.DEBUG)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
