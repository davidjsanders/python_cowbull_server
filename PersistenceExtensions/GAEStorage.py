from google.cloud import storage
from google.oauth2 import service_account
from Persistence.AbstractPersister import AbstractPersister
import google.auth


class Persister(AbstractPersister):
    def __init__(self, bucket=None, credentials_file=None, project=None):
        super(Persister, self).__init__()
        self.handler.module = "GAEStorage"
        self._validate(
            bucket=bucket,
            credentials_file=credentials_file,
            project=project
        )
        self._authenticate(
            bucket=bucket,
            credentials_file=credentials_file,
            project=project
        )
        self._get_bucket(bucket=bucket)

    def _validate(self, bucket=None, credentials_file=None, project=None):
        if bucket is None:
            self.handler.log(
                message="*** NO BUCKET PASSED! ***"
            )
            raise ValueError("Bucket name must be provided to the persister.")
        if credentials_file is not None and project is None:
            self.handler.log(
                message="*** NO CREDENTIALS AND PROJECT IS NONE! ***"
            )
            raise ValueError("Project must be provided if credentials file is provided!")

    def _authenticate(self, bucket=None, credentials_file=None, project=None):
        if credentials_file is not None:
            self.handler.log(message="Setting credentials from file")
            self.credentials = service_account.Credentials \
                .from_service_account_file(credentials_file)
            self.storage_client = storage.Client(
                credentials=self.credentials,
                project=project
            )
        else:
            self.handler.log(message="Using default credentials")
            self.credentials, project = google.auth.default()
            self.storage_client = storage.Client()

    def _get_bucket(self, bucket=None):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket)

    def _get_blob(self, key=None):
        if not key:
            raise ValueError("_get_blob: key is none.")
        if not isinstance(key, str):
            raise TypeError("_get_blob: Non-string key passed.")

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
        return blob

    def _get_blob_content(self, blob=None):
        if not blob:
            raise ValueError("_get_blob_content: blob is none.")
        self.handler.log(message="Fetching game data from blob")
        try:
            downloaded_string = blob.download_as_string()
        except Exception as e:
            self.handler.log(
                message="Exception raised while downloading blob as string: {}"
                .format(str(e))
            )
        self.handler.log(
            message="Key data retrieved -> {}".format(downloaded_string)
        )
        return downloaded_string

    def _set_blob_content(self, blob=None, content=None):
        if not blob:
            raise ValueError("_get_blob_content: blob is none.")
        if not content:
            raise ValueError("_get_blob_content: content is none.")
        if not isinstance(content, str):
            raise TypeError("_get_blob: Non-string content passed.")

        self.handler.log(message="Uploading key with value {}".format(content))
        blob.upload_from_string(
            data=content,
            content_type="application/json"
        )
        self.handler.log(message="Completed upload")

    def load(self, key=None):
        super(Persister, self).load(key=key)
        blob = self._get_blob(key=key)
        downloaded_string = self._get_blob_content(blob=blob)
        return downloaded_string

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)
        blob = self._get_blob(key=key)
        self._set_blob_content(blob=blob, content=jsonstr)
