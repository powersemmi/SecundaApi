import asyncio
import logging
from typing import cast

from hypercorn.asyncio import serve
from hypercorn.config import Config
from hypercorn.typing import ASGIFramework

from api.app import create_app
from api.settings import settings

logger = logging.getLogger(__name__)

config = Config()
config.workers = settings.WORKERS
config.bind = settings.BIND
config.accesslog = logger
config.alpn_protocols = ["h3", "h2", "http/1.1"]

app = cast(ASGIFramework, create_app())
asyncio.run(serve(app, config, mode="asgi"))
