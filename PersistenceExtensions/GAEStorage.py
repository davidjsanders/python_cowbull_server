from flask_helpers.ErrorHandler import ErrorHandler
from google.cloud import storage
from google.cloud.storage import Blob
from io import StringIO
from io import BytesIO
from Persistence.AbstractPersister import AbstractPersister
from six import text_type

# import cloudstorage


class Persister(AbstractPersister):
    def __init__(self, bucket=None, credentials_file=None):
        super(Persister, self).__init__()

        self.handler.module="GAEStorage"
        self.handler.log(message="Validating if credentials are defined or if defaults should be used")

        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket("dasander-cowbull-save-games")

    def load(self, key=None):
        super(Persister, self).load(key=key)
        blob = self.bucket.blob(key)
        return blob.download_as_string()

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)
        blob = self.bucket.blob(key)
        blob.upload_from_string(jsonstr)
