from django.urls import path, include
from web.views import account, home, project, manage, wiki, file, setting, issues

app_name = 'web'

urlpatterns = [
    path('index/', home.index, name='index'),      # 首页

    # 项目管理
    path('project/list/', project.project_list, name='project_list'),   # 项目管理页
    path('project/star/<str:project_type>/<int:project_id>/', project.project_star, name='project_star'),   # 创建星标
    path('project/unstar/<str:project_type>/<int:project_id>/', project.project_unstar, name='project_unstar'),   # 取消星标

    # 项目详细概览
    # path('manage/<int:project_id>/dashboard/', manage.dashboard, name='dashboard'),   # 项目概览
    # path('manage/<int:project_id>/issues/', manage.issues, name='issues'),   # 项目问题
    # path('manage/<int:project_id>/statistics/', manage.statistics, name='statistics'),   # 项目统计
    # path('manage/<int:project_id>/file/', manage.file, name='file'),   # 项目文件
    # path('manage/<int:project_id>/wiki/', manage.wiki, name='wiki'),   # 项目wiki
    # path('manage/<int:project_id>/settings/', manage.settings, name='settings'),   # 项目设置

    # 项目详细概览 -- 亦可
    path('manage/<int:project_id>/', include(([
            path('dashboard/', manage.dashboard, name='dashboard'),   # 项目概览
            path('statistics/', manage.statistics, name='statistics'),   # 项目统计

            # 文件路由
            path('file/', file.file, name='file'),   # 项目文件
            path('file/delete/', file.file_delete, name='file_delete'),   # 删除项目文件
            path('file/post/', file.file_post, name='file_post'),   # 客户端文件上传写入服务端
            path('file/download/', file.file_download, name='file_download'),   # 文件下载
            path('cos/cos_credentials/', file.cos_credentials, name='cos_credentials'),   # 项目文件上传授权

            # wiki路由
            path('wiki/', wiki.wiki, name='wiki'),   # 项目wiki
            path('wiki/add/', wiki.wiki_add, name='wiki_add'),   # 项目wiki添加
            path('wiki/modify/<int:wiki_id>/', wiki.wiki_modify, name='wiki_modify'),   # 项目wiki修改
            path('wiki/delete/<int:wiki_id>/', wiki.wiki_delete, name='wiki_delete'),   # 项目wiki删除
            path('wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),   # 项目wiki目录
            path('wiki/upload_img/', wiki.wiki_upload_img, name='wiki_upload_img'),   # 项目wiki图片上传
            # path('wiki/detail/', wiki.wiki_detail, name='wiki_detail'),   # 项目wiki详细

            # 项目设置
            path('settings/', setting.settings, name='settings'),   # 项目设置
            path('settings/delete/', setting.settings_delete, name='settings_delete'),   # 项目删除

            # 项目问题
            path('issues/', issues.issues, name='issues'),  # 项目问题
            path('issues/detail/<int:issues_id>/', issues.issues_detail, name='detail'),  # 项目问题详细
            path('issues/record/<int:issues_id>/', issues.issues_record, name='issues_record'),  # 项目操作记录

            ], 'manage',), namespace='manage')
         ),   # 项目设置

    # account 账户管理模块相关链接
    path('register/', account.register, name='register'),    # 用户注册
    path('login/sms/', account.login_sms, name='login_sms'),    # 用户短信登录
    path('login/', account.login, name='login'),    # 用户账号密码登录
    path('logout/', account.logout, name='logout'),    # 用户退出
    path('sms/', account.sms, name='sms'),      # 手机短信处理
    path('image/code/', account.image_code, name='image_code'),      # 获取图片验证码
]
