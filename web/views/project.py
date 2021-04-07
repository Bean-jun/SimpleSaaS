from django.shortcuts import render, redirect
from django.urls import reverse


def project_list(request):
    """项目列表"""

    # 这部分的校验移送到中间件，避免每个视图函数都需要写
    # session = request.session.get('user_id')
    # if not session:
    #     return redirect(reverse('web:index'))

    return render(request, 'web/project_list.html')