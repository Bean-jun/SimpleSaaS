from django.db import models


class UserInfo(models.Model):
    username = models.CharField(max_length=32, verbose_name="用户名", db_index=True)   # db_index 创建索引
    email = models.EmailField(max_length=32, verbose_name="邮箱")
    mobile_phone = models.CharField(max_length=32, verbose_name="手机号")
    password = models.CharField(max_length=32, verbose_name="密码")
