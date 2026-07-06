import logging
from rich.logging import RichHandler

FORMAT = "[%(name)s] %(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("twitch-bot")

def component(name: str) -> logging.Logger:
    return logging.getLogger(name)
