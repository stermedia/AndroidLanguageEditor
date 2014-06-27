import hashlib
import random
import json
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
import time
from ale.forms import ImportFileForm, RemoveShareForm
from ale.io_views import export_project, import_project
from ale.models import Project, Share
from ale.views import modify_project_cell, get_project_cells_json

__author__ = 'johniak'


def share_project(request, project_path):
    if request.method != 'POST':
        return redirect('/project/' + project_path + '/')
    project = get_object_or_404(Project, name=project_path, owner=request.user)
    share = Share()
    share.project = project
    share.hash = request.user.username + '/' + project.name + '/' + hashlib.sha1(
        str(random.random()) + request.user.username + str(
            int(round(time.time() * 1000)))).hexdigest()
    share.save()
    return HttpResponse(json.dumps({'hash': share.hash}), mimetype="application/json")


def get_shares(request, project_path):
    project = get_object_or_404(Project, name=project_path, owner=request.user)
    shares = Share.objects.filter(project=project)
    shares = [ob.as_json() for ob in shares]
    return HttpResponse(json.dumps(shares), mimetype="application/json")


def remove_share(request, project_path):
    if request.method != 'POST':
        return redirect('/project/' + project_path + '/')
    form = RemoveShareForm(request.POST)
    if not form.is_valid():
        raise Http404
    project = get_object_or_404(Project, name=project_path, owner=request.user)
    Share.objects.filter(project=project, hash=form.cleaned_data['hash']).delete()
    return HttpResponse(json.dumps({'ok': True}), mimetype="application/json")


def show_shared_project(request, hash_key):
    project = get_object_or_404(Project, hashes__hash=hash_key)
    return render(request, 'shared-project.html',
                  {'import_form': ImportFileForm(), 'project_path': project.name, 'hash_key': hash_key})


def get_json_shared_cells(request, hash_key):
    project = Project.objects.get(hashes__hash=hash_key)
    return get_project_cells_json(project)


def modify_shared_project_cell(request, hash_key):
    project = get_object_or_404(Project, hashes__hash=hash_key)
    return modify_project_cell(request, project)


def import_shared_project(request, hash_key):
    project = get_object_or_404(Project, hashes__hash=hash_key)
    import_project(request, project)
    return redirect('/share/' + hash_key)


def export_shared_project(request, hash_key):
    project = get_object_or_404(Project, hashes__hash=hash_key)
    return export_project(project)