from loguru import logger
import json


def configure_logger():
    logger.remove()

    def serialize(record):
        subset = {"timestamp": record["time"].timestamp(), "message": record["message"],
                  "severity": record["level"].name, **record["extra"]}
        return json.dumps(subset)

    def sink(message):
        serialized = serialize(message.record)
        print(serialized)

    logger.add(sink)
