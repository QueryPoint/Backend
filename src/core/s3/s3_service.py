import boto3
from botocore.config import Config
from src.config.config import config


class S3Service:
    def __init__(self):
        self.bucket_name = config.s3.BUCKET_NAME
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=config.s3.ENDPOINT_URL,
                aws_access_key_id=config.s3.ACCESS_KEY_ID,
                aws_secret_access_key=config.s3.ACCESS_SECRET_KEY,
                region_name=config.s3.REGION,
                config=Config(s3={"addressing_style": "path"}),
            )
        return self._client

    def upload_file(self, file_content: bytes, file_path: str) -> bool:
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=file_path, Body=file_content)
            return True
        except Exception as e:
            print(f"S3 upload error: {e}")
            return False

    def generate_presigned_url(self, file_path: str, expires_in: int = 300) -> str | None:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=expires_in,
            )
        except Exception as e:
            print(f"S3 presigned URL error: {e}")
            return None

    def delete_file(self, file_path: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception as e:
            print(f"S3 delete error: {e}")
            return False

    def get_file(self, file_path: str) -> bytes | None:
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response["Body"].read()
        except Exception as e:
            print(f"S3 get error: {e}")
            return None

s3_service = S3Service()