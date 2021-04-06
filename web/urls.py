from django.urls import path
from web.views import account


app_name = 'web'

urlpatterns = [
    path('register/', account.register, name='register'),    # 用户注册
    path('sms/', account.sms, name='sms'),      # 手机短信处理
]
