from django.utils.deprecation import MiddlewareMixin

from web import models


class AuthMiddleware(MiddlewareMixin):
    """用户验证中间件"""

    def process_request(self, request):
        """若是用户已经登录，则request中赋值"""
        user_id = request.session.get('user_id', 0)

        user_obj = models.UserInfo.objects.filter(id=user_id).first()

        request.tracer = user_obj