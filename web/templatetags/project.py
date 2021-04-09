from django.template import Library

from web import models


register = Library()


# 这部分实现类似全局显示
@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 获取自己创建所有的项目
    create_project_list = models.Project.objects.filter(create_user=request.tracer.user)

    # 获取自己参见的所有项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)

    return {'create': create_project_list, 'join': join_project_list}