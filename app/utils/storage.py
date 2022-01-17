import typing
import os
import logging

import pyheif
import boto3
from PIL import Image
from botocore.exceptions import ClientError
from botocore.client import BaseClient

from app.core.config import settings

s3_client = boto3.client(
    's3',
    region_name=settings.BOTO3_REGION,
    aws_access_key_id=settings.BOTO3_ACCESS_KEY,
    aws_secret_access_key=settings.BOTO3_SECRET_KEY
)


def convert_heic_to_png(file) -> Image:
    heif_file = pyheif.read(file)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.format = "jpg"
    return image


def upload_file(file_name: str, bucket: str, object_name: str, s3_client: BaseClient=s3_client) -> bool:
    """Upload a file to an S3 bucket
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
    a = upload_file("auth.py", 'ddakkm-public', 'images/asd.py', s3_client)
