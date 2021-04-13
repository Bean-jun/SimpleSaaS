import datetime

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from web import models


class Tracer:
    """封装user和price_policy的数据，便于视图函数访问"""

    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None  # 将项目进行封装


class AuthMiddleware(MiddlewareMixin):
    """用户验证中间件"""

    def process_request(self, request):
        """若是用户已经登录，则request中赋值"""

        request.tracer = Tracer()

        user_id = request.session.get('user_id', 0)

        user_obj = models.UserInfo.objects.filter(id=user_id).first()

        request.tracer.user = user_obj

        # 白名单，没有登录的用户也可以直接访问的URL
        """
        1、获取当前用户访问的URL
        2、判断当前URL是否在白名单中，若是直接访问，否则判断用户是否登录
        3、用户未登录直接返回登录页面
        """
        if request.path in settings.WHITE_REGEX_URL_LIST:
            # 中间件返回为空表示验证通过，可以直接进行访问
            return

        # 校验用户是否登录，若是未登录直接返回登录界面
        if not request.tracer.user:
            return redirect(reverse('web:login'))

        # 用户登录成功，这部分将用户的额度获取并封装到request
        # 获取用户最近的一次交易记录，ID值越大越近
        _object = models.Transaction.objects.filter(user=user_obj, status=2).order_by('-id').first()

        # 判断权限已经过期
        current_datetime = datetime.datetime.now()
        if _object.end_time and _object.end_time < current_datetime:
            # 账户权限过期
            _object = models.Transaction.objects.filter(user=user_obj, status=2, price_policy__category=1).first()

        request.tracer.price_policy = _object.price_policy

    def process_view(self, request, view, args, kwargs):
        """
        判断URL是否以manage开头
            若是判断项目ID是否为当前用户创建或者参与
        """

        # 项目路径
        if not request.path.startswith('/manage/'):
            return

        # 项目ID
        project_id = kwargs.get('project_id')

        # 判断是否为我创建或者我参加的
        project_obj = models.Project.objects.filter(create_user=request.tracer.user, id=project_id).first()
        if project_obj:
            request.tracer.project = project_obj
            return

        project_user_obj = models.ProjectUser.objects.filter(user=request.tracer.user, id=project_id).first()
        if project_user_obj:
            request.tracer.project = project_user_obj.project
            return

        # 若是都不满足，重定向到项目管理页面
        return redirect(reverse('web:project_list'))
