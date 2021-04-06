import hashlib
from django.conf import settings


def md5(value):
    """
    md5加密
    @param value: 需要加密的内容
    @return: value
    """
    hash_object = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    hash_object.update(value.encode('utf-8'))

    return hash_object.hexdigest()