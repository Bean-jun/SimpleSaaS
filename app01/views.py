import re
import random

from django.conf import settings
from django.core.validators import RegexValidator   # 正则校验数据
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from utils.tencent.sms import send_sms_single
from django.views.decorators.csrf import csrf_exempt
from django_redis import get_redis_connection


@csrf_exempt    # 避免csrf阻止
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

        phone_num = request.POST.get('user_phone')
        tpl = request.POST.get('tpl')

        # 校验数据
        if not all([phone_num, tpl]):
            return HttpResponse('发送失败')

        # 校验发送注册还是登录验证码
        if tpl not in ['register', 'login']:
            return HttpResponse('发送失败')

        # 校验手机号
        try:
            phone_num = re.match(r'^1[3-9]\d{9}$', phone_num).group(0)
        except Exception as e:
            return HttpResponse("发送失败")

        ###############################################################
        # todo : 这部分只是拦截短信的  到这一步就校验成功了，避免浪费，直接return

        random_code = random.randrange(1000, 9999)
        client = get_redis_connection('default')
        client.set(phone_num, random_code, ex=60)
        res = "{}----{}--{}-发送成功".format(phone_num, tpl, random_code)
        return JsonResponse({"msg": res, "code": 200})
        ###############################################################

        # template_id = settings.TEMPLATE_ID.get(tpl)
        # if not template_id:
        #     return HttpResponse("模板ID不存在")
        #
        # random_code = random.randrange(1000, 9999)
        #
        # template_param_list = [random_code]
        # res = send_sms_single(phone_num=phone_num,
        #                       template_id=template_id,
        #                       template_param_list=template_param_list)
        #
        # if res.get('result') == 0:
        #     return HttpResponse('发送成功')
        # else:
        #     return HttpResponse('发送失败')

from django import forms
from app01.models import UserInfo


class RegisterForm(forms.ModelForm):
    # form表单中没有手 机号的校验，故使用此方式
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^1|3|4|5|6|7|8|9\d{9}', "手机号格式错误")])

    # 修改密码表单表现形式，由可见变为不可见
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput(  # 在init中初始化后就不需要再写了
                                   attrs={'class': 'form-control','placeholder': "请输入密码"}))

    confirm_password = forms.CharField(label='重复密码',
                                       widget=forms.PasswordInput(  # 在init中初始化后就不需要再写了
                                           attrs={'class': 'form-control','placeholder': "请重复密码"}))

    verify_code = forms.CharField(label="验证码",
                                  widget=forms.TextInput(   # 在init中初始化后就不需要再写了
                                      attrs={'class': 'form-control','placeholder': "请输入验证码"}))

    class Meta:
        model = UserInfo
        fields = "__all__"

    # 上表单中每个都需要添加属性{'class': 'form-control','placeholder': } 故直接在初始化中做即可
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # name : 对应到RegisterForm中的各个字段
            # field : 对应到name字段的对象内容
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = "请输入{}".format(field.label)


@csrf_exempt    # 避免csrf阻止
def register(request):
    '''
    用户注册
    @param request:
    @return:
    '''
    if request.method == 'GET':
        # 请求登录界面
        form = RegisterForm()
        print(request.path)

        return render(request, 'app01/register.html', {'form': form})

    elif request.method == 'POST':
        # 获取请求数据校验
        result = RegisterForm(request.POST)

        client = get_redis_connection('default')

        if result.is_valid():
            # 获取验证码查看是否正确
            mobile_phone = result.cleaned_data.get('mobile_phone')
            code = result.cleaned_data.get('verify_code')

            # 获取正确验证码
            verify_code = client.get(mobile_phone)

            if verify_code == code:
                return HttpResponse('校验成功')
            else:
                return HttpResponse("验证码失效")
        else:
            print('no')

        return render(request, 'app01/register.html')
