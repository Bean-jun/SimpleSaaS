import os
import sys
import django

# 配置路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将路径添加到环境中
sys.path.append(base_dir)

# 加载项目
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SaaS.settings')

# 启动django
django.setup()

# 对models进行处理
from Scripts import user, product

# 创建用户并添加价格策略内容
user.user_init()
# 创建SaaS产品策略表
product.peoduct_init()