"""Centralized logging configuration."""
import logging
import os
import sys


def setup_logging():
    level = os.environ.get("DOMETIC_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )
    return logging.getLogger("dometic")
