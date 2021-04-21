from SaaS import settings
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def delete_file(region='ap-shanghai'):
    """文件删除"""
    secret_id = settings.TENCENT_SECRET_ID      # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY      # 替换为用户的 secretKey
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    # 获取桶列表
    response = client.list_buckets(
    )

    print(response)

    response = client.delete_object(
        Bucket='test-1305490799',
        Key='test01.png',
    )


if __name__ == '__main__':
    delete_file()
