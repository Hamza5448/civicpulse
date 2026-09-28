import json
import logging

from app.core.logging import JsonFormatter, request_id_context


def test_json_logs_include_context_request_id() -> None:
    token = request_id_context.set("request-123")
    try:
        record = logging.LogRecord("civicpulse", logging.WARNING, __file__, 1, "fallback", (), None)
        payload = json.loads(JsonFormatter().format(record))
    finally:
        request_id_context.reset(token)
    assert payload["request_id"] == "request-123"
