import logging

from google.cloud import storage


def get_filtered_species_from_remote(filtered_species_filename: str) -> set[str]:

    storage_client = storage.Client()

    bucket = storage_client.bucket("birding-il-rare-bird-excludes-de72b11720035de4")

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(filtered_species_filename)

    contents = blob.download_as_bytes().decode("utf-8")

    lines = [a.strip() for a in contents.splitlines()]

    return set(lines)


def get_filtered_species(filtered_species_filename: str) -> set[str]:
    return get_filtered_species_from_remote(filtered_species_filename)
