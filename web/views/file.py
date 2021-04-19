from django.http import JsonResponse
from django.shortcuts import render
from web.forms.file import FileFolderModelForm
from web.models import FileRepository
from utils.tencent.cos import delete_file, delete_file_list
from utils.tencent.cos import credentials


def file(request, project_id):
    """文件列表&添加文件夹"""

    folder_id = request.GET.get('folder', None)
    try:
        folder_id = int(folder_id)
        parent_obj = FileRepository.objects.filter(id=folder_id,
                                                   file_type=2,
                                                   project=request.tracer.project).first()
    except Exception as e:
        parent_obj = None

    if request.method == 'GET':

        # 路径导航
        breadcrumb_list = []
        parent = parent_obj
        while parent:
            breadcrumb_list.append({'id': parent.id, 'name': parent.name})
            parent = parent.parent

        breadcrumb_list.reverse()

        # 查看当前目录下的全部文件夹 & 文件
        queryset = FileRepository.objects.filter(project=request.tracer.project)

        if parent_obj:
            # 其他目录
            file_obj_list = queryset.filter(parent=parent_obj).order_by('-file_type')
        else:
            # 根目录
            file_obj_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        # 用于生成模态框表单
        form = FileFolderModelForm(request, parent_obj)

        context = {
            'form': form,
            'file_obj_list': file_obj_list,
            'breadcrumb_list': breadcrumb_list,
        }
        return render(request, 'web/file.html', context)

    if request.method == 'POST':
        # 文件夹的添加和修改

        # 前端传递fid过来，为空就是添加，有值就是修改
        fid = request.POST.get('fid', None)

        try:
            edit_obj = FileRepository.objects.filter(id=int(fid), file_type=2, project=request.tracer.project).first()
        except Exception as e:
            edit_obj = None

        if edit_obj:
            form = FileFolderModelForm(request, parent_obj, data=request.POST, instance=edit_obj)
        else:
            form = FileFolderModelForm(request, parent_obj, data=request.POST)

        if form.is_valid():
            form.instance.update_user = request.tracer.user
            form.instance.project = request.tracer.project
            form.instance.file_type = 2
            form.instance.parent = parent_obj
            form.save()
            return JsonResponse({'code': 200})

        return JsonResponse({'code': 416, 'msg': form.errors})


def file_delete(request, project_id):
    if request.method == "GET":
        # 获取文件ID
        fid = request.GET.get('fid', None)
        # 删除文件或者文件夹
        delete_obj = FileRepository.objects.filter(id=fid, project=request.tracer.project).first()

        if delete_obj.file_type == 1:
            # 删除文件，需要释放cos

            # 将容量释放
            request.tracer.project.use_space -= delete_obj.file_size
            request.tracer.project.save()

            # cos中删除文件
            delete_file(bucket=request.tracer.project.bucket,
                        key=delete_obj.key,
                        region=request.tracer.project.region)

            # 数据库文件删除
            delete_obj.delete()

            return JsonResponse({'code': 200})

        else:
            # 删除文件夹及文件夹内的文件
            total_size = 0
            key_list = []  # 文件名列表
            folder_list = [delete_obj]

            for folder in folder_list:
                child_list = FileRepository.objects.filter(project=request.tracer.project,
                                                           child=folder).order_by('-file_type')

                for child in child_list:
                    if child.file_type == 1:
                        # 表示文件夹
                        folder_list.append(child)
                    else:
                        # 表示是文件
                        total_size += child.file_size
                        key_list.append({"Key": child.key})
            # 删除文件
            delete_file_list(bucket=request.tracer.project.bucket,
                             key_list=key_list,
                             region=request.tracer.project.region)

            # 释放空间
            request.tracer.project.use_space -= total_size
            request.tracer.project.save()

            # 删除文件夹
            delete_obj.delete()

            return JsonResponse({'code': 200})


def cos_credentials(request, project_id):
    """获取文件上传凭证"""
    data = credentials(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse(data)