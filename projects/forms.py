from django import forms

from team_finder.mixins import GitHubUrlMixin

from .constants import STATUS_CHOICES
from .models import Project


class ProjectForm(GitHubUrlMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "status": forms.Select(choices=STATUS_CHOICES),
        }
