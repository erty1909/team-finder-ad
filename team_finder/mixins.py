from django import forms


class GitHubUrlMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url and "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub.")
        return url
