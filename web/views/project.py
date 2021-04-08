from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web import models
from web.forms.project import ProjectForm


def project_list(request):
    """项目列表"""

    # 这部分的校验移送到中间件，避免每个视图函数都需要写
    # session = request.session.get('user_id')
    # if not session:
    #     return redirect(reverse('web:index'))
    if request.method == 'GET':

        # 用户创建项目
        form = ProjectForm(request)

        # 查看项目列表
        """
        1、从数据库中获取数 
            自己创建的：已星标、未星标
            自己参与的：已星标、未星标
        2、提取已经星标
            列表 = [我创建的已星标]+[我参与的已星标]
        3、三个列表
            星标、创建、未星标    
        """
        project_dict = {'star': [],
                        'create': [],
                        'join': []
                        }

        # 创建的项目
        create_project_list = models.Project.objects.filter(create_user=request.tracer.user)
        for row in create_project_list:
            if row.star:
                project_dict['star'].append(row)
            else:
                project_dict['create'].append(row)

        # 参与的项目
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append(item.project)
            else:
                project_dict['join'].append(item.project)

        return render(request, 'web/project_list.html', {'form': form, 'project_dict': project_dict})

    if request.method == "POST":
        form = ProjectForm(request, request.POST)

        if form.is_valid():
            # 验证成功： 数据库需要存储项目名，颜色，描述，创建者

            # form表单中没有create_user,需要手动添加
            form.instance.create_user = request.tracer.user

            # 创建项目
            form.save()

            return JsonResponse({"code": 200, "msg": 'ok'})

        return JsonResponse({"code": 406, "msg": form.errors})