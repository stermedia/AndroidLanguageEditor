from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Project(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    owner = models.ForeignKey(User)
    name = models.CharField(max_length="250")

    def as_json(self):
        return dict(owner=self.owner.username,
                    name=self.name)


class Language(models.Model):
    name = models.CharField(max_length="10")
    project = models.ForeignKey(Project)


class Cell(models.Model):
    key = models.TextField()
    value = models.TextField()
    language = models.ForeignKey(Language)


class Share(models.Model):
    hash = models.CharField(max_length="390")
    project = models.ForeignKey(Project, related_name="hashes")

    def as_json(self):
        return dict(hash=self.hash,
                    project=self.project.as_json(), )