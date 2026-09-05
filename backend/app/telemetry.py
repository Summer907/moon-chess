import json
import logging

logger = logging.getLogger("moon_chess")
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
logger.propagate = False


def event(name: str, **fields: object) -> None:
    logger.info(json.dumps({"event": name, **fields}, separators=(",", ":")))
