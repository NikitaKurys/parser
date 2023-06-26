import logging
from datetime import datetime
from logging import FileHandler, Formatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = FileHandler(f'logs/{datetime.now().strftime("%Y_%m_%d")}_parser.log',
                      encoding="windows-1251")
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)
