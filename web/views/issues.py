from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from utils.pagination import Pagination
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm
from web.models import Issues, IssuesReply


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
