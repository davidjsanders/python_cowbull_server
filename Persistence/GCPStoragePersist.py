from google.cloud import storage


class GCPStoragePersist:

    def __init__(self, bucket=None):
        if not bucket:
            raise ValueError('A bucket name must be provided!')
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(bucket_name=bucket)
        if not self.bucket:
            self.bucket = self.storage_client.create_bucket(bucket_name=bucket)


    def save(self, key=None, jsonstr=None):
        if key is None:
            raise ValueError("Key must be present to persist game.")
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")
        blob = self.bucket.blob(key)
        blob.upload_from_string(str(jsonstr), content_type="application/json")

    def load(self, key=None):
        if key is None:
            raise ValueError("Key must be present to execute_load game")
        blob = self.bucket.blob(key)
        return_result = blob.download_as_string()
        if return_result is not None:
            if isinstance(return_result, bytes):
                return_result = str(return_result.decode('utf-8'))
        return return_result
