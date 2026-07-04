import json
import logging

from studyguard.logging_conf import JsonFormatter


def test_json_formatter_emits_valid_json():
    record = logging.LogRecord("svc", logging.INFO, "file.py", 10, "hello %s", ("world",), None)
    data = json.loads(JsonFormatter().format(record))
    assert data["message"] == "hello world"
    assert data["level"] == "INFO"
    assert data["logger"] == "svc"
