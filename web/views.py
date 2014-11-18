import json
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from packingcheck.s3 import s3_storage


def index(request):
    return render(request, 'index.html', {})


def check_list(request):
    user_id = _user(request)
    l = []
    if user_id:
        prefix = 'packingcheck/%s/' % user_id
        l = [{'name': name[len(prefix):]} for name in s3_storage.list(settings.S3_BUCKET, prefix)]

    return HttpResponse(json.dumps(l))


def add_list(request):
    user_id = _user(request)
    list_name = request.POST.get('list-name')
    print user_id, list_name
    if user_id and list_name:
        key = 'packingcheck/%s/%s' % (user_id, list_name)
        if not s3_storage.exists(settings.S3_BUCKET, key):
            s3_storage.put(settings.S3_BUCKET, key, json.dumps([]))
    return redirect('/')


def check_items(request):
    return ''


def _user(request):
    user_id = request.COOKIES.get('userID')
    return user_id


def items(request):
    return render(request, 'items.html', {})