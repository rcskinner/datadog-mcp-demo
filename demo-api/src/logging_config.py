import json
import logging


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": self.formatTime(record),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        for attr in ("dd.trace_id", "dd.span_id", "dd.service", "dd.env", "dd.version"):
            val = getattr(record, attr, None)
            if val:
                log[attr] = val
        return json.dumps(log)


def configure():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)
