import logging

import google_crc32c
from google.cloud import secretmanager

LOG = logging.getLogger(__name__)

_client = secretmanager.SecretManagerServiceClient()


def get_current_version_of_text_secret(secret_name: str):

    secret_path = f"projects/397747986563/secrets/{secret_name}/versions/current"

    result = None

    try:
        response = _client.access_secret_version(request={"name": secret_path})

        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)

        if response.payload.data_crc32c == int(crc32c.hexdigest(), 16):
            result = response.payload.data.decode("UTF-8")
        else:
            LOG.error("CRC check on secret \"%s\" failed", secret_name)

    except:
        LOG.error("Error fetching secret \"%s\"", secret_name, exc_info=1)

    finally:
        if not result:
            raise Exception(f"No secret {secret_name} available")
        
    return result
