from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_STUDENT = "student"
    ROLE_TEACHER = "teacher"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = (
        (ROLE_STUDENT, "Ученик"),
        (ROLE_TEACHER, "Преподаватель"),
        (ROLE_ADMIN, "Администратор"),
    )

    role = models.CharField(
        "Роль",
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
    )
    phone = models.CharField("Телефон", max_length=30, blank=True)
    # Используем FileField, чтобы не зависеть от Pillow (ImageField требует Pillow)
    avatar = models.FileField("Аватар", upload_to="avatars/", blank=True, null=True)

    def __str__(self) -> str:
        full_name = (self.get_full_name() or "").strip()
        return full_name or self.username
