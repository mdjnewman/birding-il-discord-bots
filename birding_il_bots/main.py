import logging.config
from pathlib import Path
import asyncio
from .agree_bot import client as agree_bot
from .rba_bot import client as rba_bot
from .token_provider import get_token_for_bot

source_path = Path(__file__).resolve()
source_dir = source_path.parent


logging.config.fileConfig(Path(source_dir / "logging.ini"))

LOG = logging.getLogger(__name__)


agree_bot_token = get_token_for_bot("agree")
rba_bot_token = get_token_for_bot("rba")


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(rba_bot.start(rba_bot_token))
loop.create_task(agree_bot.start(agree_bot_token))
loop.run_forever()
