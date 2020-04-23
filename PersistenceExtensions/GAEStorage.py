from flask_helpers.ErrorHandler import ErrorHandler
from google.auth.credentials import Credentials
from google.cloud import storage
from google.cloud.storage import Blob
from google.oauth2 import service_account
from Persistence.AbstractPersister import AbstractPersister


import google.auth

# import cloudstorage


class Persister(AbstractPersister):
    def __init__(self, bucket=None, credentials_file=None, project=None):
        if bucket is None:
            raise ValueError("Bucket name must be provided to the persister.")
        if credentials_file is not None and project is None:
            raise ValueError("Project must be provided if credentials file is provided!")

        super(Persister, self).__init__()

        self.handler.module="GAEStorage"
        self.handler.log(message="Validating if credentials are defined or if defaults should be used")
        if credentials_file is not None:
            self.handler.log(message="Setting credentials")
            self.credentials = service_account.Credentials.from_service_account_file(credentials_file)
            self.storage_client = storage.Client(
                credentials=self.credentials,
                project=project
            )
        else:
            self.handler.log(message="Using default credentials")
            self.credentials, project = google.auth.default()
            self.storage_client = storage.Client()

        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket("dasander-cowbull-save-games")

    def load(self, key=None):
        super(Persister, self).load(key=key)
        blob = self.bucket.blob(key)
        return blob.download_as_string()

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)
        blob = self.bucket.blob(key)
        blob.upload_from_string(
            data=jsonstr,
            content_type="application/json"
        )
