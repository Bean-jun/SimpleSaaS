import random

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from utils.tencent.sms import send_sms_single
from web import models
from web.models import UserInfo


class RegisterForm(forms.ModelForm):
    # form表单中没有手机号的校验，故使用此方式
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^1|3|4|5|6|7|8|9\d{9}', "手机号格式错误")])

    # 修改密码表单表现形式，由可见变为不可见
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput())

    confirm_password = forms.CharField(label='重复密码',
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


class SendSmsForm(forms.Form):
    """用户注册码内容校验"""
    # mobile_phone  = forms.CharField(label='手机号',
    #                                validators=[RegexValidator(r'^1|3|4|5|6|7|8|9\d{9}', "手机号格式错误")])
    mobile_phone = forms.CharField(label='手机号')
    # 这部分将用户的request直接初始化过来
    def __init__(self, request, *args, **kwargs):
        super(SendSmsForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """手机号钩子"""
        mobile_phone = self.cleaned_data['mobile_phone']

        # 校验数据库中是否存在已有手机号
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()

        if exists:
            raise ValidationError("手机号已经存在")

        # 判断模板ID是否存在
        tpl = self.request.POST.get('tpl')
        template_id = settings.TEMPLATE_ID.get(tpl)

        if not template_id:
            raise ValidationError("短信模板错误")

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