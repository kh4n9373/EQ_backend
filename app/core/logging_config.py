import logging
import sys
from app.core.config import settings


def setup_logging():
    root = logging.getLogger()
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)
    
    level = ( settings.log_level or "INFO").upper()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    root.setLevel(level)
    root.addHandler(console_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING if settings.environment == "prod" else logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)