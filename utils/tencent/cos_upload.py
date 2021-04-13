from django.conf import settings
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def upload_file(bucked, region='ap-shanghai'):
    """文件上传"""
    secret_id = settings.TENCENT_SECRET_ID      # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY      # 替换为用户的 secretKey
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    # 创建桶
    client.create_bucket(Bucket=bucked)

    return client


