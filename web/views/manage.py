from django.shortcuts import render


def statistics(request, project_id):
    return render(request, 'web/statistics.html')
