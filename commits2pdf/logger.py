from logging import getLogger, INFO, StreamHandler, Formatter

logger = getLogger()
logger.setLevel(INFO)
console = StreamHandler()
formatter = Formatter("%(asctime)s | %(levelname)s - %(message)s", datefmt="%H:%M:%S")
console.setFormatter(formatter)
logger.addHandler(console)