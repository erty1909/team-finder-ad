import json

from django.test import Client, TestCase, override_settings
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
class UserAuthTests(TestCase):
    def test_register_and_login(self):
        client = Client()
        response = client.post(
            reverse("users:register"),
            {
                "name": "Test",
                "surname": "User",
                "email": "test@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

        client.logout()
        response = client.post(
            reverse("users:login"),
            {"email": "test@example.com", "password": "password123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("projects:list"))

    def test_login_invalid_credentials(self):
        User.objects.create_user(
            email="test@example.com",
            name="Test",
            surname="User",
            password="password123",
        )
        response = self.client.post(
            reverse("users:login"),
            {"email": "test@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный имейл или пароль")


@override_settings(DATABASES=TEST_DATABASES)
class SkillTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="dev@example.com",
            name="Dev",
            surname="Eloper",
            password="password123",
        )
        self.skill = Skill.objects.create(name="Python")
        self.client.login(username="dev@example.com", password="password123")

    def test_skills_autocomplete(self):
        Skill.objects.create(name="PostgreSQL")
        response = self.client.get(reverse("users:skills_autocomplete"), {"q": "P"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data), 10)
        names = [item["name"] for item in data]
        self.assertIn("PostgreSQL", names)
        self.assertIn("Python", names)

    def test_add_skill_by_id(self):
        response = self.client.post(
            reverse("users:add_skill", kwargs={"user_id": self.user.id}),
            data=json.dumps({"skill_id": self.skill.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["added"])
        self.assertFalse(payload["created"])
        self.assertTrue(self.user.skills.filter(pk=self.skill.pk).exists())

    def test_add_skill_by_name(self):
        response = self.client.post(
            reverse("users:add_skill", kwargs={"user_id": self.user.id}),
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["added"])
        self.assertTrue(payload["created"])
        self.assertTrue(Skill.objects.filter(name="Django").exists())

    def test_add_skill_duplicate(self):
        self.user.skills.add(self.skill)
        response = self.client.post(
            reverse("users:add_skill", kwargs={"user_id": self.user.id}),
            data=json.dumps({"skill_id": self.skill.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["added"])

    def test_remove_skill(self):
        self.user.skills.add(self.skill)
        response = self.client.post(
            reverse(
                "users:remove_skill",
                kwargs={"user_id": self.user.id, "skill_id": self.skill.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.skills.filter(pk=self.skill.pk).exists())

    def test_remove_skill_not_assigned(self):
        response = self.client.post(
            reverse(
                "users:remove_skill",
                kwargs={"user_id": self.user.id, "skill_id": self.skill.id},
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_add_skill_forbidden_for_other_user(self):
        other = User.objects.create_user(
            email="other@example.com",
            name="Other",
            surname="User",
            password="password123",
        )
        response = self.client.post(
            reverse("users:add_skill", kwargs={"user_id": other.id}),
            data=json.dumps({"skill_id": self.skill.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)


@override_settings(DATABASES=TEST_DATABASES)
class UsersListTests(TestCase):
    def setUp(self):
        self.python = Skill.objects.create(name="Python")
        self.react = Skill.objects.create(name="React")
        self.alice = User.objects.create_user(
            email="alice@example.com",
            name="Alice",
            surname="One",
            password="password123",
        )
        self.bob = User.objects.create_user(
            email="bob@example.com",
            name="Bob",
            surname="Two",
            password="password123",
        )
        self.alice.skills.add(self.python)
        self.bob.skills.add(self.react)

    def test_filter_users_by_skill(self):
        response = self.client.get(reverse("users:list"), {"skill": "Python"})
        self.assertEqual(response.status_code, 200)
        participants = response.context["participants"]
        emails = [u.email for u in participants.object_list]
        self.assertIn("alice@example.com", emails)
        self.assertNotIn("bob@example.com", emails)
        self.assertEqual(response.context["active_skill"], "Python")

    def test_users_list_pagination(self):
        for i in range(15):
            User.objects.create_user(
                email=f"user{i}@example.com",
                name=f"User{i}",
                surname="Test",
                password="password123",
            )
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, 200)
        participants = response.context["participants"]
        self.assertEqual(len(participants.object_list), 12)
        self.assertTrue(participants.has_next())

        response = self.client.get(reverse("users:list"), {"page": 2})
        self.assertEqual(len(response.context["participants"].object_list), 5)
