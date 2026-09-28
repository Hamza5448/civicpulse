import json
import logging
import sys
from contextvars import ContextVar

request_id_context: ContextVar[str] = ContextVar("request_id", default="system")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", request_id_context.get()),
        }
        for field in ("complaint_id", "provider", "error_class"):
            value = getattr(record, field, None)
            if value:
                payload[field] = value
        return json.dumps(payload)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
