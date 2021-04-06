import random
import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection

from web.forms.account import RegisterForm, SendSmsForm


def register(request):
    # 创建form表单用于用于注册
    form = RegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'web/register.html', context)


from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def sms(request):
    """
    # 发送手机验证码
    ?tpl=login --> 914045
    ?tpl=register --> 914010
    @param request:
    @param phone_num:
    @return:
    """
    if request.method == 'POST':

        # 获取内容
        form = SendSmsForm(request, request.POST)

        if form.is_valid():
            # 都放在is_valid的钩子中处理
                # 数据验证成功，进行短信发送
                # 写入到redis
            return JsonResponse({'code': 200, 'msg': 'ok'})
        else:
            return JsonResponse({'code': 416, 'msg': form.errors})

            # -------------------- 除form校验的方式以外的内容 -------------
            # # 校验数据
            # if not all([phone_num, tpl]):
            #     return HttpResponse('发送失败')
            #
            # # 校验发送注册还是登录验证码
            # if tpl not in ['register', 'login']:
            #     return HttpResponse('发送失败')
            #
            # # 校验手机号
            # try:
            #     phone_num = re.match(r'^1[3-9]\d{9}$', phone_num).group(0)
            # except Exception as e:
            #     return HttpResponse("发送失败")

