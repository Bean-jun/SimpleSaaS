from SaaS import settings
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def upload_file(region='ap-shanghai'):
    """文件上传"""
    secret_id = settings.TENCENT_SECRET_ID      # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY      # 替换为用户的 secretKey
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    # 获取桶列表
    response = client.list_buckets(
    )

    print(response)

    response = client.upload_file(
        Bucket='test-1305490799',
        LocalFilePath='./test.png',
        Key='picture.png',
    )
    print(response['ETag'])


if __name__ == '__main__':
    upload_file()
