import json
import logging

logger = logging.getLogger("moon_chess")


def event(name: str, **fields: object) -> None:
    logger.info(json.dumps({"event": name, **fields}, separators=(",", ":")))
