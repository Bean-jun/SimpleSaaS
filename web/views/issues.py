import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from utils.pagination import Pagination
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm
from web.models import Issues, IssuesReply, ProjectUser


def issues(request, project_id):
    """问题栏"""
    if request.method == "GET":
        form = IssuesModelForm(request)

        issues_obj = Issues.objects.filter(project=request.tracer.project)

        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=issues_obj.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=3,
        )
        issues_object_list = issues_obj[page_object.start:page_object.end]

        context = {
            'form': form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html()
        }
        return render(request, 'web/issues.html', context)

    if request.method == "POST":
        form = IssuesModelForm(request, data=request.POST)

        if form.is_valid():
            # 添加问题数据
            form.instance.project = request.tracer.project
            form.instance.create_user = request.tracer.user

            form.save()

            return JsonResponse({'code': 200})

        return JsonResponse({'msg': form.errors, 'code': 416})


def issues_detail(request, project_id, issues_id):
    """问题详细"""
    issues_obj = Issues.objects.filter(id=issues_id, project_id=project_id).first()
    form = IssuesModelForm(request, instance=issues_obj)

    context = {
        "form": form,
        'issues_obj': issues_obj,
    }
    return render(request, 'web/issues_detail.html', context)


@csrf_exempt
def issues_record(request, project_id, issues_id):
    """问题的记录"""
    if request.method == "GET":
        reply_list = IssuesReply.objects.filter(issues__project_id=project_id, issues_id=issues_id)

        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'create_user': row.create_user.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)

        return JsonResponse({'code': 200, 'msg': data_list})

    if request.method == "POST":
        """评论回复"""
        form = IssuesReplyModelForm(request.POST)

        if form.is_valid():
            form.instance.issues_id = issues_id
            form.instance.reply_type = 2
            form.instance.create_user = request.tracer.user
            instance = form.save()
            data = {
                'id': instance.id,
                'reply_type_text': instance.get_reply_type_display(),
                'content': instance.content,
                'create_user': instance.create_user.username,
                'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': instance.reply_id
            }
            return JsonResponse({'code': 200, 'msg': data})

        return JsonResponse({'code': 416, 'msg': "评论失败"})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    """修改详细页记录"""

    def create_reply_record(content):
        """创建记录"""
        issues_reply = IssuesReply.objects.create(
            reply_type=1,
            issues=issues_obj,
            create_user=request.tracer.user,
            content=content
        )
        data = {
            'id': issues_reply.id,
            'reply_type_text': issues_reply.get_reply_type_display(),
            'content': issues_reply.content,
            'create_user': issues_reply.create_user.username,
            'datetime': issues_reply.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': issues_reply.reply_id
        }

        return data

    post_dict = json.loads(request.body.decode('utf-8'))

    issues_obj = Issues.objects.filter(project_id=project_id, id=issues_id).first()
    name = post_dict.get('name')
    value = post_dict.get('value')

    # 获取当前字段对象
    field_obj = Issues._meta.get_field(name)
    # 1、数据库更新
    # 1.1 文本
    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if not value:
            if not field_obj.null:
                return JsonResponse({'code': 416, 'msg': '您选择的数据不可以是空哦'})
            setattr(issues_obj, name, None)
            issues_obj.save()
            change_record = "{}变更为空".format(field_obj.verbose_name)
        else:
            setattr(issues_obj, name, value)
            issues_obj.save()
            change_record = "{}变更为{}".format(field_obj.verbose_name, value)

        return JsonResponse({'code': 200, 'msg': create_reply_record(change_record)})

    # 1.2 FK字段
    if name in ['issues_type', 'module', 'parent', 'assign']:
        if not value:
            if not field_obj.null:
                return JsonResponse({'code': 416, 'msg': '您选择的数据不可以是空哦'})
            setattr(issues_obj, name, None)
            issues_obj.save()
            change_record = "{}变更为空".format(field_obj.verbose_name)
        else:
            if name == 'assign':
                # 是否是项目创建者
                if value == str(request.tracer.project.create_user_id):
                    instance = request.tracer.project.create_user
                else:
                    project_user_object = ProjectUser.objects.filter(project_id=project_id,
                                                                     user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'code': 416, 'msg': "您选择的值不存在"})

                setattr(issues_obj, name, instance)
                issues_obj.save()
                change_record = "{}更新为{}".format(field_obj.verbose_name, str(instance))  # value根据文本获取到内容

            else:
                # 判断用户输入的值是否为当前项目的信息
                instance = field_obj.remote_field.model.objects.filter(project_id=project_id, id=value).first()

                if not instance:
                    return JsonResponse({'code': 416, 'msg': '您选择的数据不存在'})

                setattr(issues_obj, name, instance)
                issues_obj.save()
                change_record = "{}变更为{}".format(field_obj.verbose_name, str(instance))

        return JsonResponse({'code': 200, 'msg': create_reply_record(change_record)})

    # 1.3 choices 字段
    if name in ['priority', 'status', 'mode']:
        selected_text = None
        for key, text in field_obj.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'code': 416, 'msg': "您选择的值不存在"})

        setattr(issues_obj, name, value)
        issues_obj.save()
        change_record = "{}更新为{}".format(field_obj.verbose_name, selected_text)
        return JsonResponse({'code': 200, 'data': create_reply_record(change_record)})

    # 1.4 m2m 字段
    if name == 'attention':
        if not isinstance(value, list):
            return JsonResponse({'code': 416, 'msg': "数据格式错误"})

        if not value:
            # 关注者为空
            issues_obj.attention.set(value)
            issues_obj.save()
            change_record = "{}更新为空".format(field_obj.verbose_name)
            return JsonResponse({'code': 200, 'data': create_reply_record(change_record)})
        else:
            # 有关注者 --- 》 判断用户是否为用户成员
            # 获取当前项目的所有成员
            user_dict = {str(request.tracer.project.create_user_id): request.tracer.project.create_user.username}
            project_user_list = ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username

            username_list = []
            for user_id in value:
                username = user_dict.get(user_id)
                if not username:
                    # 不是项目成员
                    return JsonResponse({'code': 416, 'msg': "用户不存在，请刷新"})
                username_list.append(username)

            issues_obj.attention.set(value)
            issues_obj.save()
            change_record = "{}更新为{}".format(field_obj.verbose_name, ','.join(username_list))

        return JsonResponse({'code': 200, 'data': create_reply_record(change_record)})

    return JsonResponse({'code': 416, 'msg': "error"})
