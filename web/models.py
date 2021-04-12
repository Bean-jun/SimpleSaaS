from django.db import models


class UserInfo(models.Model):
    """用户信息表"""
    username = models.CharField(max_length=32, verbose_name="用户名", db_index=True)   # db_index 创建索引
    email = models.EmailField(max_length=32, verbose_name="邮箱")
    mobile_phone = models.CharField(max_length=32, verbose_name="手机号")
    password = models.CharField(max_length=32, verbose_name="密码")


class PricePolicy(models.Model):
    """SaaS产品价格策略表"""
    CATEGORY_CHOICES = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )
    category = models.SmallIntegerField(choices=CATEGORY_CHOICES, default=2, verbose_name="收费类型")
    title = models.CharField(max_length=32, verbose_name="产品标题")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="产品价格")
    create_project = models.IntegerField(verbose_name="项目数量")
    project_member = models.IntegerField(verbose_name="成员数量")
    project_space = models.IntegerField(verbose_name="项目空间")
    single_file_space = models.IntegerField(verbose_name="单文件空间(M)")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


class Transaction(models.Model):
    """产品交易订单"""
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '已支付'),
    )
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, verbose_name="订单状态")
    user = models.ForeignKey('UserInfo', on_delete=models.CASCADE, verbose_name="用户")
    price_policy = models.ForeignKey("PricePolicy", on_delete=models.CASCADE, verbose_name="价格策略")
    count = models.IntegerField(verbose_name="产品数量(年)", help_text="0表示无期限")
    pay_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="支付价格")
    start_time = models.DateTimeField(null=True,blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    order = models.CharField(max_length=64, unique=True, verbose_name="订单号")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


class Project(models.Model):
    """项目内容"""
    COLOR_CHOICES = (
        (1, '#ff0c0a'),
        (2, '#ff0aef'),
        (3, '#1d0aff'),
        (4, '#0af4ff'),
        (5, '#1aff0a'),
        (6, '#ffeb0a'),
    )
    name = models.CharField(max_length=64, verbose_name="项目名称")
    desc = models.CharField(max_length=256, null=True, blank=True, verbose_name="描述")
    color = models.SmallIntegerField(choices=COLOR_CHOICES, verbose_name="颜色", default=1)
    star = models.BooleanField(default=False, verbose_name="星标")
    use_space = models.IntegerField(default=0, verbose_name="使用空间")

    join_count = models.IntegerField(default=1, verbose_name="参与人数")
    create_user = models.ForeignKey("UserInfo", on_delete=models.CASCADE, verbose_name="创建者")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


class ProjectUser(models.Model):
    """项目参与者"""
    project = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name="项目名称")
    user = models.ForeignKey("UserInfo", on_delete=models.CASCADE, verbose_name="用户")
    star = models.BooleanField(default=False, verbose_name="星标")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
