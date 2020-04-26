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
        self.bucket = self.storage_client.bucket(bucket)

    def load(self, key=None):
        self.handler.log(message="Calling load.super()")
        super(Persister, self).load(key=key)

        self.handler.log(message="Getting data for key {}".format(key))
        try:
            blob = self.bucket.blob(key)
        except Exception as e:
            self.handler.log(
                message="Exception raised while fetching Blob: {}"
                .format(str(e))
            )
            raise
        self.handler.log(message="Key data for key {} retrieved".format(key))

        self.handler.log(message="Fetching game data from {}".format(key))
        try:
            downloaded_string = blob.download_as_string()
        except Exception as e:
            self.handler.log(
                message="Exception raisef while downloading blob as string: {}"
                .format(str(e))
            )
        self.handler.log(message="Key data for key {} retrieved -> {}".format(key, downloaded_string))

        return downloaded_string

    def save(self, key=None, jsonstr=None):
        self.handler.log(message="Calling save.super()")
        super(Persister, self).save(key=key, jsonstr=jsonstr)
        self.handler.log(message="Calling self.bucket.blob from key {}".format(key))
        blob = self.bucket.blob(key)
        self.handler.log(message="Uploading key {} with value {}".format(key, jsonstr))
        blob.upload_from_string(
            data=jsonstr,
            content_type="application/json"
        )
        self.handler.log(message="Completed upload")
