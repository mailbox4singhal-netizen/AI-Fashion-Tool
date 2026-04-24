"""Simple structured logger — routes JSON lines to stdout.
In prod, swap for loguru/structlog + sinks.
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            payload.update(record.extra_data)
        return json.dumps(payload)


_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(JsonLineFormatter())

logger = logging.getLogger("ai_fashion")
logger.setLevel(logging.INFO)
logger.handlers = [_handler]
logger.propagate = False


def log_event(msg: str, **extra: Any) -> None:
    record = logger.makeRecord("ai_fashion", logging.INFO, "", 0, msg, (), None)
    record.extra_data = extra
    logger.handle(record)
