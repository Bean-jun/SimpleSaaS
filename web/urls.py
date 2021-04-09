from django.urls import path
from web.views import account, home, project

app_name = 'web'

urlpatterns = [
    path('index/', home.index, name='index'),      # 首页

    # 项目管理
    path('project/list/', project.project_list, name='project_list'),   # 项目管理页
    path('project/star/<str:project_type>/<int:project_id>/', project.project_star, name='project_star'),   # 创建星标
    path('project/unstar/<str:project_type>/<int:project_id>/', project.project_unstar, name='project_unstar'),   # 取消星标

    # account 账户管理模块相关链接
    path('register/', account.register, name='register'),    # 用户注册
    path('login/sms/', account.login_sms, name='login_sms'),    # 用户短信登录
    path('login/', account.login, name='login'),    # 用户账号密码登录
    path('logout/', account.logout, name='logout'),    # 用户退出
    path('sms/', account.sms, name='sms'),      # 手机短信处理
    path('image/code/', account.image_code, name='image_code'),      # 获取图片验证码
]
