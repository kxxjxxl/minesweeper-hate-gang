import os
import logging

from .cli import CLI


if __name__ == "__main__":
    log_level = os.environ.get("LOGLEVEL", "WARN").upper()
    logging.basicConfig(level=log_level)
    CLI()
