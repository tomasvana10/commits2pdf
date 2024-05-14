from logging import INFO, Formatter, StreamHandler, getLogger

logger = getLogger()
logger.setLevel(INFO)
console = StreamHandler()
formatter = Formatter("%(levelname)s: %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)
