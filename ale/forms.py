__author__ = 'johniak8'
from django import forms


class CreateProjectForm(forms.Form):
    name = forms.CharField(max_length=250, required=True)


class ImportFileForm(forms.Form):
    zipfile = forms.FileField()


class ModifyCellForm(forms.Form):
    key = forms.CharField(max_length=1000, required=True)
    value = forms.CharField(max_length=100000, required=True)
    lang = forms.CharField(max_length=250, required=True)

class RemoveShareForm(forms.Form):
    hash = forms.CharField(max_length=190, required=True)
