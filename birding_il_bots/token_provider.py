import logging
import os

from .secret_provider import get_current_version_of_text_secret

LOG = logging.getLogger(__name__)


def get_token_for_bot(bot_name: str):
    token_from_env = os.getenv(f'DISCORD_{bot_name.upper()}_BOT_TOKEN')

    if token_from_env:
        LOG.info(f"Using token for \"{bot_name}\" bot from environment")
        return token_from_env

    secret_name = f"birding-il-{bot_name}-bot-token"

    response = get_current_version_of_text_secret(secret_name)

    LOG.info(f"Using token for \"{bot_name}\" bot from Secrets Manager")

    return response
