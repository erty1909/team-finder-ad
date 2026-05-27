"""Smoke tests for all main pages and variant-2 API endpoints."""
from django.test import TestCase, override_settings
from django.urls import reverse

from projects.models import Project
from users.models import Skill, User

TEST_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


@override_settings(DATABASES=TEST_DATABASES)
class SmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="alice@example.com",
            name="Alice",
            surname="Test",
            password="password123",
            about="About me",
        )
        self.skill = Skill.objects.create(name="Python")
        self.user.skills.add(self.skill)
        self.project = Project.objects.create(
            name="Smoke Project",
            description="Desc",
            owner=self.user,
            status="open",
        )
        self.project.participants.add(self.user)

    def test_public_pages(self):
        pages = [
            reverse("projects:list"),
            reverse("projects:detail", kwargs={"project_id": self.project.id}),
            reverse("users:list"),
            reverse("users:detail", kwargs={"user_id": self.user.id}),
            reverse("users:register"),
            reverse("users:login"),
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, msg=url)

    def test_authenticated_pages(self):
        self.client.login(username="alice@example.com", password="password123")
        pages = [
            reverse("users:edit_profile"),
            reverse("users:change_password"),
            reverse("projects:create"),
            reverse("projects:edit", kwargs={"project_id": self.project.id}),
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, msg=url)

    def test_users_list_context(self):
        response = self.client.get(reverse("users:list"), {"skill": "Python"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("participants", response.context)
        self.assertIn("all_skills", response.context)
        self.assertEqual(response.context["active_skill"], "Python")

    def test_user_detail_has_skills_block(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"user_id": self.user.id})
        )
        self.assertContains(response, "Навыки")
        self.assertContains(response, "Python")

    def test_logout_redirects(self):
        self.client.login(username="alice@example.com", password="password123")
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, reverse("projects:list"))

    def test_change_password(self):
        self.client.login(username="alice@example.com", password="password123")
        response = self.client.post(
            reverse("users:change_password"),
            {
                "old_password": "password123",
                "new_password1": "newpass456",
                "new_password2": "newpass456",
            },
        )
        self.assertRedirects(
            response,
            reverse("users:detail", kwargs={"user_id": self.user.id}),
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass456"))

    def test_edit_profile_phone_validation(self):
        self.client.login(username="alice@example.com", password="password123")
        response = self.client.post(
            reverse("users:edit_profile"),
            {
                "name": "Alice",
                "surname": "Test",
                "about": "Updated",
                "phone": "89991234567",
                "github_url": "https://github.com/alice",
            },
        )
        self.assertRedirects(
            response,
            reverse("users:detail", kwargs={"user_id": self.user.id}),
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79991234567")

    def test_pagination_template_present(self):
        for i in range(15):
            User.objects.create_user(
                email=f"extra{i}@example.com",
                name=f"Extra{i}",
                surname="User",
                password="password123",
            )
        response = self.client.get(reverse("users:list"))
        self.assertContains(response, "pagination")
