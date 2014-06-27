import random
import zipfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from ale.forms import CreateProjectForm, ImportFileForm, ModifyCellForm, RemoveShareForm
from ale.io_views import import_project, export_project
from ale.models import Project, Language, Cell, Share
import json
import time
from lxml import objectify
import xml.etree.ElementTree as ET
import hashlib


def sign_in(request):
    if request.user.is_authenticated():
        return redirect('/')
    if request.method == 'GET':
        return render(request, 'sign_in.html',
                      {'form': AuthenticationForm()})
    form = AuthenticationForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'sign_in.html',
                      {'form': AuthenticationForm(), 'error_message': 'Wrong input data. <br>' + str(form.errors)})
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            if request.GET.get('next') is not None:
                return redirect(request.GET.get('next'))
            else:
                return redirect('/')
        else:
            return render(request, 'sign_in.html',
                          {'form': AuthenticationForm(), 'error_message': 'User account is not active.'})
    else:
        return render(request, 'sign_in.html',
                      {'form': AuthenticationForm(), 'error_message': 'Invalid username or password.'})


@login_required
def log_out(request):
    logout(request)
    return redirect('/signin/')


def sign_up(request):
    if request.user.is_authenticated():
        return redirect('/')
    if request.method == 'GET':
        return render(request, 'sign_up.html',
                      {'form': UserCreationForm()})
    form = UserCreationForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'sign_up.html',
                      {'form': UserCreationForm(),
                       'error_message': 'Wrong input data. <br>' + str(form.errors)})

    users_count = User.objects.filter(username=form.clean_username()).count()
    if users_count != 0:
        return render(request, 'sign_up.html',
                      {'form': UserCreationForm(),
                       'error_message': 'User with selected username already exists.'})

    user = User()
    user.username = form.clean_username()
    user.set_password(form.clean_password2())
    user.save()
    return redirect('/signin/')


@login_required
def dashboard(request):
    projects = Project.objects.filter(owner=request.user)
    if projects.count() > 0:
        return show_user_project(request, projects[0].name)
    return render(request, 'project.html',
                  {'create_project_form': CreateProjectForm()})


@login_required
def show_user_project(request, project_path):
    get_object_or_404(Project, name=project_path, owner=request.user)
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'project.html',
                  {'import_form': ImportFileForm(), 'project_path': project_path, 'projects': projects})


@login_required
def cells_data_json(request, project_path):
    project = get_object_or_404(Project, name=project_path, owner=request.user)
    return get_project_cells_json(project)


def get_project_cells_json(project):
    langs = Language.objects.filter(project=project)
    cells_dict = dict()
    for lang in langs:
        cells = Cell.objects.filter(language=lang)
        fill_dict(cells, cells_dict)
    return HttpResponse(cells_dict2json(langs, cells_dict), mimetype="application/json")


def fill_dict(cells, cells_dict):
    for cell in cells:
        if not cell.key in cells_dict:
            cells_dict[cell.key] = dict()
        cells_dict[cell.key][cell.language.name] = cell


def cells_dict2json(langs, cells_dict):
    items = []
    for key in cells_dict:
        item = dict()
        item_dict = dict()
        item_dict['key'] = key
        for lang in langs:
            if not lang.name in cells_dict[key]:
                item_dict[lang.name] = ""
            else:
                item_dict[lang.name] = cells_dict[key][lang.name].value
        item['id'] = key
        item['values'] = item_dict
        items.append(item)
    meta = []
    d = dict()
    d['name'] = 'key'
    d['label'] = 'key'
    d['datatype'] = 'string'
    d['editable'] = False
    meta.append(d)
    for lang in langs:
        d = dict()
        d['name'] = lang.name
        d['label'] = lang.name
        d['datatype'] = 'string'
        d['editable'] = True
        meta.append(d)
    return json.dumps({'metadata': meta, 'data': items})


@login_required
def create_project(request):
    if request.method == 'GET':
        raise Http404
    form = CreateProjectForm(request.POST)
    if not form.is_valid():
        return render(request, 'dashboard.html',
                      {'form': UserCreationForm(),
                       'error_message': 'Wrong input data. <br>' + str(form.errors)})
    project_count = Project.objects.filter(name=form.cleaned_data['name'], owner=request.user).count()
    if project_count != 0:
        return render(request, 'dashboard.html',
                      {'form': UserCreationForm(),
                       'error_message': 'Specified project already exists.'})

    project = Project()
    project.name = form.cleaned_data['name']
    project.owner = request.user
    project.save()
    return redirect('/project/' + project.name + "/")


@login_required
def modify_cell(request, project_path):
    if request.method != 'POST':
        raise Http404
    project = get_object_or_404(Project, name=project_path, owner=request.user)
    return modify_project_cell(request, project)


def modify_project_cell(request, project):
    form = ModifyCellForm(request.POST)
    if not form.is_valid():
        return HttpResponse(json.dumps({'error': 'form is not valid'}), mimetype="application/json")

    cell_count = Cell.objects.filter(language__name=form.cleaned_data['lang'], language__project=project,
                                     key=form.cleaned_data['key']).count()
    if cell_count > 1:
        return HttpResponse(json.dumps({'error': 'specified cell doesn\'t exists ' + str(cell_count)}),
                            mimetype="application/json")
    cell = Cell()
    if cell_count == 1:
        cell = Cell.objects.get(language__name=form.cleaned_data['lang'], language__project=project,
                                key=form.cleaned_data['key'])
    if cell_count == 0:
        cell.key = form.cleaned_data['key']
        cell.language = Language.objects.get(name=form.cleaned_data['lang'], project=project)
    cell.value = form.cleaned_data['value']
    cell.save()
    return HttpResponse(json.dumps({'ok': True}), mimetype="application/json")



