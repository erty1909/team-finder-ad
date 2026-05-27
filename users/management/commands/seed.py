"""
Management command to populate the DB with test users and projects.
Usage: python manage.py seed
"""
from django.core.management.base import BaseCommand
from users.models import User, Skill
from projects.models import Project


SKILLS = ["Python", "Django", "React", "TypeScript", "PostgreSQL", "Docker", "Figma", "Go"]

USERS = [
    dict(email="alice@example.com", name="Alice", surname="Ivanova",
         about="Backend developer, love Python & Django", password="password123"),
    dict(email="bob@example.com",   name="Bob",   surname="Petrov",
         about="Frontend wizard, React & TypeScript fan", password="password123"),
    dict(email="maria@example.com", name="Maria", surname="Sidorova",
         about="Full-stack & DevOps enthusiast",         password="password123"),
]

PROJECTS = [
    dict(owner_email="alice@example.com", name="OpenTasker",
         description="Open-source task tracker built with Django REST + React.",
         status="open"),
    dict(owner_email="alice@example.com", name="PyScheduler",
         description="Lightweight job scheduler library for Python.",
         status="closed"),
    dict(owner_email="bob@example.com",   name="PortfolioGen",
         description="Auto-generate beautiful portfolio sites from a YAML config.",
         status="open"),
    dict(owner_email="maria@example.com", name="DockerDash",
         description="Real-time dashboard for monitoring Docker containers.",
         status="open"),
]


class Command(BaseCommand):
    help = "Seed database with test users, skills and projects"

    def handle(self, *args, **options):
        # Skills
        skills = {}
        for sname in SKILLS:
            skill, _ = Skill.objects.get_or_create(name=sname)
            skills[sname] = skill
        self.stdout.write(f"  Skills: {len(skills)}")

        # Users
        users = {}
        skill_map = {
            "alice@example.com": ["Python", "Django", "PostgreSQL"],
            "bob@example.com":   ["React", "TypeScript", "Figma"],
            "maria@example.com": ["Python", "Docker", "Go"],
        }
        for ud in USERS:
            email = ud["email"]
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                self.stdout.write(f"  User already exists: {email}")
            else:
                user = User.objects.create_user(
                    email=email,
                    name=ud["name"],
                    surname=ud["surname"],
                    about=ud.get("about", ""),
                    password=ud["password"],
                )
                self.stdout.write(f"  Created user: {email}")
            for sname in skill_map.get(email, []):
                user.skills.add(skills[sname])
            users[email] = user

        # Projects
        for pd in PROJECTS:
            owner = users[pd["owner_email"]]
            project, created = Project.objects.get_or_create(
                name=pd["name"],
                owner=owner,
                defaults=dict(description=pd["description"], status=pd["status"]),
            )
            if created:
                project.participants.add(owner)
                self.stdout.write(f"  Created project: {pd['name']}")
            else:
                self.stdout.write(f"  Project already exists: {pd['name']}")

        # Add some participants cross-projects
        try:
            alice = users["alice@example.com"]
            bob   = users["bob@example.com"]
            maria = users["maria@example.com"]
            p1 = Project.objects.get(name="OpenTasker")
            p1.participants.add(bob)
            p3 = Project.objects.get(name="DockerDash")
            p3.participants.add(alice)
        except Project.DoesNotExist:
            pass

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
