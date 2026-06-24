from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models

from .constants import ABOUT_MAX_LENGTH, NAME_MAX_LENGTH, PHONE_MAX_LENGTH
from .managers import UserManager
from .utils import generate_avatar_image


class Skill(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    surname = models.CharField(max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, blank=True, null=True, unique=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, blank=True, related_name="users")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        first_letter = self.name[0] if self.name else "U"
        png_bytes = generate_avatar_image(first_letter)
        if png_bytes:
            safe = self.email.replace("@", "_").replace(".", "_")
            self.avatar.save(f"avatar_{safe}.png", ContentFile(png_bytes), save=False)
