from django.shortcuts import render


def dashboard(request, project_id):
    return render(request, 'web/dashboard.html')


def issues(request, project_id):
    return render(request, 'web/issues.html')


def statistics(request, project_id):
    return render(request, 'web/statistics.html')


def file(request, project_id):
    return render(request, 'web/file.html')


def wiki(request, project_id):
    return render(request, 'web/wiki.html')


def settings(request, project_id):
    return render(request, 'web/settings.html')