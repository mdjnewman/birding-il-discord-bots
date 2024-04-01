import logging
import os

import google_crc32c
from google.cloud import secretmanager

LOG = logging.getLogger(__name__)


def get_token(bot_name: str):
    token_from_env = os.getenv(f'DISCORD_{bot_name.upper()}_BOT_TOKEN')

    if token_from_env:
        LOG.info(f"Using token for \"{bot_name}\" bot from environment")
        return token_from_env

    client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/397747986563/secrets/birding-il-{bot_name}-bot-token/versions/current"

    response = client.access_secret_version(request={"name": secret_name})
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)

    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        LOG.error(f"CRC check on token for \"{bot_name}\" bot from secrets manager failed")
    else:
        LOG.info(f"Using token for \"{bot_name}\" bot from secrets manager")
        payload = response.payload.data.decode("UTF-8")
        return payload

    raise Exception(f"No available token for {bot_name}")
