from utils.encrypt import md5
from web import models


def user_init():
    models.UserInfo.objects.create(username='豆子',
                                   email='1056001451@qq.com',
                                   mobile_phone='13735202686',
                                   password=md5('100100100'))
