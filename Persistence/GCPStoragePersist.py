from flask_helpers.ErrorHandler import ErrorHandler
from io import StringIO
from io import BytesIO
from six import text_type

import googleapiclient.discovery
import googleapiclient.http
import json
import tempfile


class GCPStoragePersist:

    def __init__(self, bucket=None):
        if not bucket:
            raise ValueError('A bucket name must be provided!')

        self.handler = ErrorHandler(
            module="GCPStoragePersist",
            method="__init__"
        )

        self.handler.log(message="Requesting storage client.", status=0)
        self.storage_client = googleapiclient.discovery.build(
            'storage',
            'v1',
            cache_discovery=False
        )
        self.handler.log(message="Setting bucket to {}".format(bucket), status=0)
        self.bucket = bucket

        self.handler.log(message="Loading configuration from environment.", status=0)

    def save(self, key=None, jsonstr=None):
        self.handler.method = "save"
        self.handler.log(message="In GCPStoragePersist - save method. Validating inputs.")

        if key is None:
            raise ValueError("Key must be present to persist game.")
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")

        contents = StringIO(initial_value=text_type(jsonstr))

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
        self.handler.log(message="Executing GCP Storage request", status=0)
        try:
            resp = req.execute()
            print(resp)
        except Exception as e:
            print(e)
        self.handler.log(message="Closed temp file/stream with game data", status=0)

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
        except Exception as e:
            self.handler.log(message="Exception: {}".format(repr(e)))

        return return_result


        return_result = contents.read()
        contents.close()
        self.handler.log(message="Returning result: {}".format(return_result))
        return return_result
