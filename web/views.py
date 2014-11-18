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

    if user_id and list_name:
        key = _list_key(list_name, user_id)
        if not s3_storage.exists(settings.S3_BUCKET, key):
            s3_storage.put(settings.S3_BUCKET, key, json.dumps([]))
    return redirect('/')


def _user(request):
    user_id = request.COOKIES.get('userID')
    return user_id


def _list_key(list_name, user_id):
    return 'packingcheck/%s/%s' % (user_id, list_name)


def _get_list_items(key):
    list_items = []
    list_items_data = s3_storage.get(settings.S3_BUCKET, key)
    if list_items_data:
        list_items = json.loads(list_items_data)
    return list_items


def items(request):
    user_id = _user(request)
    list_name = request.GET.get('list-name')
    list_items = []
    key = _list_key(list_name, user_id)
    if user_id and list_name:
        list_items = _get_list_items(key)

    return render(request, 'items.html', {
        'name': list_name,
        'items': list_items})


def add_item(request):
    user_id = _user(request)
    list_name = request.POST.get('list-name')
    item_name = request.POST.get('item-name')

    if all((user_id, list_name, item_name)):
        key = _list_key(list_name, user_id)
        list_items = _get_list_items(key)

        if item_name not in list_items:
            list_items.append(item_name)
            s3_storage.put(settings.S3_BUCKET, key, json.dumps(list_items))

    if list_name:
        return redirect('/items?list-name=%s' % list_name)
    else:
        return redirect('/')




