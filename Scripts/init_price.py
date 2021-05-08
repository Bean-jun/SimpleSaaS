import os
import sys
import django

# 配置路径
from web import models

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将路径添加到环境中
sys.path.append(base_dir)

# 加载项目
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SaaS.settings')

# 启动django
django.setup()

# 对models进行处理
models.PricePolicy.objects.create(
    title='VIP',
    price=100,
    create_project=50,
    project_member=10,
    project_space=10,
    single_file_space=500,
    category=2
)

models.PricePolicy.objects.create(
    title='SVIP',
    price=200,
    create_project=150,
    project_member=110,
    project_space=110,
    single_file_space=1024,
    category=2
)

models.PricePolicy.objects.create(
    title='SSVIP',
    price=500,
    create_project=550,
    project_member=510,
    project_space=510,
    single_file_space=2048,
    category=2
)
