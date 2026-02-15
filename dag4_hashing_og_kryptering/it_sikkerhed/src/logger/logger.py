import logging
from pythonjsonlogger import jsonlogger 
from pathlib import Path

LOG_FILE = Path("app_log.ndjson")
    
handler = logging.FileHandler(LOG_FILE)
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
)
handler.setFormatter(formatter)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(handler)


def _flush():
    for h in LOGGER.handlers:
        h.flush()

def _read_file():
    return LOG_FILE.read_text()

def _clean_log():
    if LOG_FILE.exists():
        LOG_FILE.write_text("")


LOGGER.flush = _flush
LOGGER.read_file = _read_file
LOGGER.clean_log = _clean_log