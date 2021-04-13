from django.conf import settings
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def create_bucket(bucket, region="ap-shanghai"):
    """创建桶"""
    config = CosConfig(Region=region, SecretId=settings.TENCENT_SECRET_ID, SecretKey=settings.TENCENT_SECRET_KEY)
    client = CosS3Client(config)
    client.create_bucket(
        Bucket=bucket,
        ACL="public-read"  # private  /  public-read / public-read-write
    )


def upload_file(bucket, key, image_obj, region):
    """文件上传"""
    config = CosConfig(Region=region, SecretId=settings.TENCENT_SECRET_ID, SecretKey=settings.TENCENT_SECRET_KEY)
    client = CosS3Client(config)

    client.upload_file_from_buffer(Bucket=bucket,
                                   Key=key,
                                   Body=image_obj)

    return f'https://{bucket}.cos.{region}.myqcloud.com/{key}'



