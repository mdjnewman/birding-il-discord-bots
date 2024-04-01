#!/usr/bin/env python3


import logging.config
from pathlib import Path

from .agree_bot import client as agree_bot
from .token_provider import get_token_for_bot

source_path = Path(__file__).resolve()
source_dir = source_path.parent


logging.config.fileConfig(Path(source_dir / "logging.ini"))

LOG = logging.getLogger(__name__)


agree_bot_token = get_token_for_bot("agree")
agree_bot.run(agree_bot_token, log_handler=None)
