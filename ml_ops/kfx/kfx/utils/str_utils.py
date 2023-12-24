import logging

def remove_prefix(cloud_uri : str, prefix : str):
    """
    Removes the prefix from the string.

    Args:
        cloud_uri: The gcs or bq uri.
        prefix: only 'gs://' or 'bq://' are supported.
    """

    assert prefix == "gs://" or prefix == "bq://"

    if cloud_uri.startswith(prefix):
        cloud_uri = cloud_uri[len(prefix):]
    return cloud_uri

def write_file(content : str, uri : str):
    """
    Writes content to a local file uri
    Args:
        content: content to write to a local file.
        uri: uri of file to save content.
    """
    logging.info(f"Writing content to {uri}")
    
    with open(uri, "w") as f:
        f.write(content)
    