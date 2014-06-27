import StringIO
import os
from django.http import HttpResponse, Http404

__author__ = 'johniak'
import zipfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from ale.forms import ImportFileForm
from ale.models import Project, Language, Cell
import time
from lxml import objectify
from lxml import etree


@login_required
def import_user_project(request, project_path):
    if request.method != 'POST':
        raise Http404
    project = get_object_or_404(Project, name=project_path, owner=request.user)
    import_project(request, project)
    return redirect('/project/' + project_path + "/")


@login_required
def export_user_project(request, project_path):
    project = get_object_or_404(Project, name=project_path, owner=request.user)
    return export_project(project)


def import_project(request, project):
    form = ImportFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'project.html',
                      {'import_form': ImportFileForm(), 'import_file_error_message': str(form.errors)})
    if form.cleaned_data['zipfile'].name[-4:] != '.zip':
        return render(request, 'project.html',
                      {'import_form': ImportFileForm(),
                       'import_file_error_message': 'file must be in zip format not in ' + form.cleaned_data['zipfile'].
                                                                                           name[-1:-5]})
    filename = handle_uploaded_file(form.cleaned_data['zipfile'], project)
    parse_zip_file(filename, project)
    os.remove(filename)


def parse_zip_file(path, project):
    with zipfile.ZipFile(path, 'r') as android_zip:
        dirs = [x[:-1] for x in android_zip.namelist() if x.endswith('/')]
        langs_filenames = [x for x in android_zip.namelist() if x.endswith('lang.xml') and x[:x.find('/')] in dirs]
        dirs = [x[:x.find('/')] for x in langs_filenames]
        langs_names = [x[x.rfind('-') + 1:] for x in dirs if x != 'values']
        langs_names.insert(langs_filenames.index('values/lang.xml'), 'default')
        Cell.objects.filter(language__project=project).delete()
        Language.objects.filter(project=project).delete()
        for index, lang_name in enumerate(langs_names):
            print index
            lang = Language()
            lang.name = lang_name
            lang.project = project
            lang.save()
            parse_lang_cells(android_zip, lang, langs_filenames[index])


def parse_lang_cells(android_zip, lang, filename):
    xml_text = android_zip.read(filename).decode('utf-8').encode('utf-8')
    root = objectify.fromstring(xml_text)
    for string_tag in root.string:
        cell = Cell()
        cell.key = string_tag.attrib['name']
        if string_tag.text is not None:
            cell.value = string_tag.text.encode('utf-8')
        cell.language = lang
        cell.save()


def handle_uploaded_file(f, project):
    path = 'tmp/' + project.name + f.name[:-4] + str(int(round(time.time() * 1000))) + '.zip'
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path


def export_project(project):
    langs = Language.objects.filter(project=project)
    xmls = []
    for lang in langs:
        cells = Cell.objects.filter(language=lang)
        xmls.append(prepare_xml(cells))
    resp = HttpResponse(createZipFile(langs, xmls).getvalue(), mimetype="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % project.name
    return resp


def prepare_xml(cells):
    xml_root = etree.Element('resources')
    for cell in cells:
        xml_cell = etree.Element('string', name=cell.key)
        xml_cell.text = cell.value
        xml_root.append(xml_cell)
    indent(xml_root, level=4)
    return xml_root


def indent(elem, level=0):
    i = "\n" + level * " "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + " "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def createZipFile(langs, xmls):
    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED)
    print langs
    print xmls
    for index, lang in enumerate(langs):
        if lang.name != 'default':
            path = os.path.join('values-' + lang.name, 'lang.xml')
        else:
            path = os.path.join('values', 'lang.xml')
        zf.writestr(path,
                    etree.tostring(xmls[index], xml_declaration=True, encoding='utf-8'))
    zf.close()
    return s