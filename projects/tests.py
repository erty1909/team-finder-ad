import json

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from projects.models import Project
from users.models import User

TEST_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


@override_settings(DATABASES=TEST_DATABASES)
class ProjectTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            name="Owner",
            surname="User",
            password="password123",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            name="Other",
            surname="User",
            password="password123",
        )
        self.project = Project.objects.create(
            name="Test Project",
            description="Description",
            owner=self.owner,
            status="open",
        )
        self.project.participants.add(self.owner)

    def test_project_list_sorted_newest_first(self):
        now = timezone.now()
        Project.objects.create(
            name="Older",
            owner=self.owner,
            status="open",
            created_at=now - timezone.timedelta(days=1),
        )
        Project.objects.create(
            name="Newer",
            owner=self.owner,
            status="open",
            created_at=now,
        )
        response = self.client.get(reverse("projects:list"))
        projects = list(response.context["projects"].object_list)
        self.assertEqual(projects[0].name, "Newer")
        self.assertEqual(projects[1].name, "Older")

    def test_project_list_pagination(self):
        for i in range(15):
            Project.objects.create(
                name=f"Project {i}",
                owner=self.owner,
                status="open",
            )
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(len(response.context["projects"].object_list), 12)
        self.assertTrue(response.context["projects"].has_next())

    def test_create_project(self):
        self.client.login(username="owner@example.com", password="password123")
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "New Project",
                "description": "About",
                "github_url": "",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="New Project")
        self.assertEqual(project.owner, self.owner)
        self.assertIn(self.owner, project.participants.all())

    def test_complete_project(self):
        self.client.login(username="owner@example.com", password="password123")
        response = self.client.post(
            reverse("projects:complete", kwargs={"project_id": self.project.id}),
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")

    def test_toggle_participate(self):
        self.client.login(username="other@example.com", password="password123")
        response = self.client.post(
            reverse("projects:toggle_participate", kwargs={"project_id": self.project.id}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["participant"])
        self.assertIn(self.other, self.project.participants.all())

        response = self.client.post(
            reverse("projects:toggle_participate", kwargs={"project_id": self.project.id}),
        )
        self.assertFalse(response.json()["participant"])
        self.assertNotIn(self.other, self.project.participants.all())

    def test_root_redirects_to_project_list(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/projects/list/", fetch_redirect_response=False)
