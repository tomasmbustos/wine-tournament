# Import the Secret Manager client library.
from google.cloud import secretmanager
import logging
import os
import json


def get_secret(project_id, secret_name, version_id):
    if version_id is None:
        version_id = "latest"
    name = "projects/{}/secrets/{}/versions/{}".format(project_id, secret_name, version_id)

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Print the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.

    payload = json.loads(response.payload.data)
    # payload = response.payload.data.decode("UTF-8")
    # print("Plaintext: {}".format(payload))
    return payload


def set_env_vars_from_gcp_secret_manager(project_id, secret_name, version_id="latest"):
    payload = get_secret(project_id, secret_name, version_id)
    for key, value in payload.items():
        logging.info(f"Setting env var {key}")
        os.environ[key] = value
