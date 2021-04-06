import random

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from utils import encrypt
from utils.tencent.sms import send_sms_single
from web import models
from web.forms.bootstrap import BootStrapForm
from web.models import UserInfo


class RegisterForm(forms.ModelForm):
    # form表单中没有手机号的校验，故使用此方式
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^1|3|4|5|6|7|8|9\d{9}', "手机号格式错误")])

    # 修改密码表单表现形式，由可见变为不可见
    password = forms.CharField(label='密码',
                               min_length=8,
                               max_length=64,
                               error_messages={
                                   'min_length': '密码不可以少于8位',
                                   'max_length': '密码不可以大于64位'
                               },
                               widget=forms.PasswordInput())

    confirm_password = forms.CharField(label='重复密码',
                                       min_length=8,
                                       max_length=64,
                                       error_messages={
                                           'min_length': '重复密码不可以少于8位',
                                           'max_length': '重复密码不可以大于64位'
                                       },
                                       widget=forms.PasswordInput())

    verify_code = forms.CharField(label="验证码")

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

    def clean_username(self):
        # 用户钩子
        username = self.cleaned_data['username']

        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            # 添加错误信息，相当于字段的error_messages
            self.add_error('username', "用于已经存在")

        return username

    def clean_mobile_phone(self):
        # 手机号钩子，校验两次数据是否相同
        mobile_phone = self.cleaned_data['mobile_phone']

        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()

        if exists:
            self.add_error('mobile_phone', "手机号已经注册")

        return mobile_phone

    def clean_password(self):
        # 处理密码加密
        password = self.cleaned_data['password']
        # 加密操作
        return encrypt.md5(password)

    def clean_confirm_password(self):
        # 密码钩子
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        # 重复密码加密用于校验
        confirm_password = encrypt.md5(confirm_password)

        if password != confirm_password:
            raise ValidationError("两次密码不一致")

        return confirm_password

    def clean_verify_code(self):
        # 验证码钩子
        verify_code = self.cleaned_data['verify_code']

        conn = get_redis_connection('default')
        code = conn.get(self.cleaned_data.get('mobile_phone'))

        if not code:
            raise ValidationError("验证码失效或者未发送,请重新获取")

        code = code.decode()

        if verify_code.strip() != code.strip():
            raise ValidationError("验证码错误")

        return verify_code


class SendSmsForm(forms.Form):
    """用户注册码内容校验"""
    mobile_phone = forms.CharField(label='手机号',
                                   min_length=11,
                                   max_length=11,
                                   error_messages={
                                       'min_length': '手机号不可以少于11位',
                                       'max_length': '手机号不可以大于11位'
                                   },
                                   validators=[RegexValidator(r'^1|3|4|5|6|7|8|9\d{9}', "手机号格式错误")])

    # 这部分将用户的request直接初始化过来
    def __init__(self, request, *args, **kwargs):
        super(SendSmsForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """手机号钩子"""
        mobile_phone = self.cleaned_data['mobile_phone']

        # 判断模板ID是否存在
        tpl = self.request.POST.get('tpl')
        template_id = settings.TEMPLATE_ID.get(tpl)

        if not template_id:
            raise ValidationError("短信模板错误")

        # 校验数据库中是否存在已有手机号
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == 'login':
            if not exists:
                raise ValidationError("手机号不存在, 请注册")
        elif tpl == 'register':
            if exists:
                raise ValidationError("手机号已经存在")

        # 数据验证成功，进行短信发送
        code = random.randrange(1000, 9999)

        # 我是穷鬼 ，这里先注释掉
        # res = send_sms_single(phone_num=mobile_phone,
        #                       template_id=template_id,
        #                       template_param_list=[code,])
        #
        # if res.get('result') != 0:
        #     raise ValidationError('发送失败{}'.format(res.get('errmsg')))

        # 写入到redis
        conn = get_redis_connection('default')
        conn.set(mobile_phone, code, ex=60)

        return mobile_phone


class LoginSMSForm(BootStrapForm, forms.Form):
    """用户短信登录校验"""
    mobile_phone = forms.CharField(label='手机号',
                                   min_length=11,
                                   max_length=11,
                                   error_messages={
                                       'min_length': '手机号不可以少于11位',
                                       'max_length': '手机号不可以大于11位'
                                   },
                                   validators=[RegexValidator(r'^1|3|4|5|6|7|8|9\d{9}', "手机号格式错误")])
    verify_code = forms.CharField(label="验证码")

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']

        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if not exists:
            self.add_error('mobile_phone', "手机号不存在, 请注册")

        return mobile_phone

    def clean_verify_code(self):
        # 验证码钩子
        verify_code = self.cleaned_data['verify_code']
        mobile_phone = self.cleaned_data['mobile_phone']

        # 手机号不存在，无需校验
        if not mobile_phone:
            return verify_code

        conn = get_redis_connection('default')
        code = conn.get(self.cleaned_data.get('mobile_phone'))

        if not code:
            raise ValidationError("验证码失效或者未发送,请重新获取")

        code = code.decode()

        if verify_code.strip() != code.strip():
            raise ValidationError("验证码错误")

        return verify_code


class LoginForm(BootStrapForm, forms.Form):
    """用户短信登录校验"""
    username = forms.CharField(label='手机号',
                               min_length=2,
                               max_length=64,
                               error_messages={
                                   'min_length': '密码不可以少于2位',
                                   'max_length': '密码不可以大于64位'
                               })
    password = forms.CharField(label='密码',
                               min_length=8,
                               max_length=64,
                               error_messages={
                                   'min_length': '密码不可以少于8位',
                                   'max_length': '密码不可以大于64位'
                               },
                               widget=forms.PasswordInput())

    verify_code = forms.CharField(label="验证码",
                                  min_length=5,
                                  max_length=5,
                                  error_messages={
                                      'min_length': '密码不可以少于5位',
                                      'max_length': '密码不可以大于5位'
                                  })

    def __init__(self,request, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        """密码钩子"""
        password = self.cleaned_data['password']

        # 返回直接加密好的密码
        return encrypt.md5(password)

    def clean_verify_code(self):
        """验证码钩子验证"""
        verify_code = self.cleaned_data['verify_code']

        # 获取session中的code
        session_verify_code = self.request.session.get('image_code')
        if not session_verify_code:
            raise ValidationError("验证码已经过期，请重新获取")

        if verify_code.strip().upper() != session_verify_code.strip().upper():
            raise ValidationError("验证码输入错误")

        return verify_code
