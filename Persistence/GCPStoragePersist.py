from flask_helpers.ErrorHandler import ErrorHandler
from io import StringIO
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from six import text_type

import googleapiclient.discovery
import googleapiclient.http
import os


class GCPStoragePersist:

    #TODO : Refine error checking and logging

    def _load_credentials(self):
        self.handler.log(message="Getting authentication credentials")

    def __init__(self, bucket=None):
        if not bucket:
            raise ValueError('A bucket name must be provided!')

        self.handler = ErrorHandler(
            module="GCPStoragePersist",
            method="__init__",
        )

        self.handler.log(message="Validating if credentials are defined or if defaults should be used")
        secret_name = "/cowbull/secrets/k8storageservice.json"
        if not os.path.isfile(secret_name):
            self.handler.log(message="Requesting storage client with default credentials.", status=0)
            self.storage_client = googleapiclient.discovery.build('storage', 'v1', cache_discovery=False)
        else:
            self.handler.log(message="Requesting storage client with secret credentials.", status=0)
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                secret_name,
                ["https://www.googleapis.com/auth/compute"]
            )
            self.handler.log(message="Credentials received: {}".format(credentials))
            self.storage_client = googleapiclient.discovery.build(
                'storage',
                'v1',
                credentials=credentials,
                cache_discovery=False
            )
            self.handler.log(message="Storage client retrieved.")


        self.handler.log(message="Storage client received. Setting bucket to {}".format(bucket), status=0)
        self.bucket = bucket

    def save(self, key=None, jsonstr=None):
        self.handler.method = "save"
        self.handler.log(message="In GCPStoragePersist - save method. Validating inputs.")

        if key is None:
            raise ValueError("Key must be present to persist game.")
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")

        contents = StringIO(initial_value=text_type(jsonstr))

        self.handler.log(message="Forming GCP Storage request")
        body = {
            'name': key,
            'contentType': 'application/json',
            'mimeType': 'application/json'
        }
        req = self.storage_client.objects().insert(
            bucket=self.bucket,
            body=body,
            media_mime_type='application/json',
            media_body=googleapiclient.http.MediaIoBaseUpload(contents, 'application/json')
        )

        self.handler.log(message="Executing GCP Storage request")
        try:
            resp = req.execute()
            print(resp)
        except Exception as e:
            self.handler.log(message="Exception: {}".format(repr(e)))

        self.handler.log(message="Closed temp file/stream with game data")

    def load(self, key=None):
        self.handler.method = "load"
        self.handler.log(message="In GCPStoragePersist - load method. Validating inputs.")

        if key is None:
            raise ValueError("Key must be present to execute_load game")

        self.handler.log(message="Creating temporary file to hold results")
        filename = '{}.tmp'.format(key)

        return_result = None
        try:
            self.handler.log(message="Opening file in write mode")
            tmpfile = BytesIO()
            self.handler.log(message="File opened")

            self.handler.log(message="Issuing get_media request on {}".format(key))
            req = self.storage_client.objects().get_media(
                bucket=self.bucket,
                object=key
            )
            self.handler.log(message="Request on {} formed".format(key))

            self.handler.log(message="Creating downloader")
            downloader = googleapiclient.http.MediaIoBaseDownload(
                tmpfile,
                req
            )
            self.handler.log(message="Downloader created")

            self.handler.log(message="Downloading from downloader")
            done = False
            while not done:
                self.handler.log(message="Fetching chunk")
                status, done = downloader.next_chunk()
                self.handler.log(message="Fetch status: {}%".format(status.progress()*100))
            self.handler.log(message="Download complete")

            self.handler.log(message="Getting JSON")
            return_result = tmpfile.getvalue()
            self.handler.log(message="JSON is {} (type {})".format(
                return_result, type(return_result)
            ))

            self.handler.log(message="Converting bytes result to unicode (if reqd)")
            if return_result is not None:
                if isinstance(return_result, bytes):
                    return_result = str(return_result.decode('utf-8'))

            self.handler.log(message="Returning result: {}".format(return_result))
        except Exception as e:
            self.handler.log(message="Exception: {}".format(repr(e)))

        return return_result
