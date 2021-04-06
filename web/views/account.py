from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from web import models
from web.forms.account import RegisterForm, SendSmsForm, LoginSMSForm, LoginForm


def register(request):
    """用户注册"""
    if request.method == "GET":
        # 创建form表单用于用于注册
        form = RegisterForm()

        context = {
            'form': form,
        }
        return render(request, 'web/register.html', context)

    if request.method == "POST":
        # 获取数据并校验
        form = RegisterForm(request.POST)

        if form.is_valid():
            # 保存数据, 但是数据密码是明文，需要在钩子中处理
            form.save()

            # 保存数据
            # data = form.cleaned_data
            # data.pop('verify_code')
            # data.pop('confirm_password')
            # models.UserInfo.objects.create(**data)

            return JsonResponse({'code': 200, 'msg': '/login/'})

        return JsonResponse({'code': 416, 'msg': form.errors})


@csrf_exempt
def sms(request):
    """发送手机验证码
    ?tpl=login --> 914045
    ?tpl=register --> 914010
    @param request:
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


def login_sms(request):
    """短信验证登录"""
    if request.method == 'GET':
        form = LoginSMSForm()

        context = {
            'form': form,
        }
        return render(request, 'web/login_sms.html', context)

    if request.method == "POST":
        form = LoginSMSForm(request.POST)

        if form.is_valid():
            # 验证成功，登录
            mobile_phone = form.cleaned_data['mobile_phone']
            user = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
            # 登录成功写入session中
            request.session['user_id'] = user.id
            request.session.set_expiry(60 * 60 * 24 * 7)

            return JsonResponse({"code": 200, "msg": '/index/'})
        else:
            return JsonResponse({"code": 406, "msg": form.errors})

def login(request):
    """用户名和密码登录"""
    if request.method == "GET":
        form = LoginForm(request)
        return render(request, 'web/login.html', {'form': form})

    if request.method == "POST":
        # 获取数据并校验
        form = LoginForm(request, request.POST)

        if form.is_valid():
            # 验证成功，登录
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # user = models.UserInfo.objects.filter(username=username, password=password).first()
            # 用户使用邮箱、手机号均可以实现登录
            user = models.UserInfo.objects.\
                filter(Q(email=username)|Q(mobile_phone=username)).filter(password=password).first()

            if user:
                # 用户账号密码正确
                # 登录成功写入session中
                request.session['user_id'] = user.id
                request.session.set_expiry(60 * 60 * 24 * 7)

                return redirect(reverse('web:index'))
            else:
                form.add_error('username', "用户名或密码错误")

        return render(request, 'web/login.html', {'form': form})


def image_code(request):
    """生成图片验证码"""
    from io import BytesIO
    from utils.image_code import check_code
    image_obj, code = check_code()

    # 将图片验证码存入内存，然后返回给用户
    stream = BytesIO()
    image_obj.save(stream, 'png')

    # 将code验证码写入到session中
    request.session['image_code'] = code
    request.session.set_expiry(60)

    return HttpResponse(stream.getvalue())


def logout(request):
    """用户退出"""
    request.session.flush()
    return redirect(reverse('web:index'))