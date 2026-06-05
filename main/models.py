from django.conf import settings
from django.db import models

from users.utils import slugify_ru


class Course(models.Model):
    AGE_3_6 = "3-6"
    AGE_7_10 = "7-10"
    AGE_11_14 = "11-14"
    AGE_15_PLUS = "15+"

    AGE_CHOICES = (
        (AGE_3_6, "3–6"),
        (AGE_7_10, "7–10"),
        (AGE_11_14, "11–14"),
        (AGE_15_PLUS, "15+"),
    )

    DIR_PAINTING = "painting"
    DIR_GRAPHICS = "graphics"
    DIR_SCULPT = "sculpt"
    DIR_MIXED = "mixed"
    DIR_COMPOSITION = "composition"

    DIRECTION_CHOICES = (
        (DIR_PAINTING, "Живопись"),
        (DIR_GRAPHICS, "Графика"),
        (DIR_SCULPT, "Лепка"),
        (DIR_MIXED, "Смешанная техника"),
        (DIR_COMPOSITION, "Композиция"),
    )

    title = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True, blank=True)
    short_description = models.CharField("Короткое описание", max_length=300)
    description = models.TextField("Описание")
    price = models.PositiveIntegerField("Цена", default=0)
    age_group = models.CharField("Возраст", max_length=20, choices=AGE_CHOICES)
    direction = models.CharField("Направление", max_length=30, choices=DIRECTION_CHOICES)
    image = models.FileField("Картинка", upload_to="courses/", blank=True, null=True)
    schedule = models.TextField("Расписание", blank=True)
    is_active = models.BooleanField("Активно", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    def save(self, *args, **kwargs):
        # Slug генерируем автоматически из названия
        if not self.slug:
            self.slug = slugify_ru(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class Enrollment(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Активна"),
        (STATUS_COMPLETED, "Завершена"),
        (STATUS_CANCELLED, "Отменена"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Ученик",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField("Дата записи", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.student} → {self.course or 'без курса'}"


class StudentWork(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "На модерации"),
        (STATUS_APPROVED, "Одобрена"),
        (STATUS_REJECTED, "Отклонена"),
    )

    TECH_OIL = "oil"
    TECH_WATERCOLOR = "watercolor"
    TECH_PENCIL = "pencil"
    TECH_PASTEL = "pastel"
    TECH_OTHER = "other"

    TECHNIQUE_CHOICES = (
        (TECH_OIL, "Масло"),
        (TECH_WATERCOLOR, "Акварель"),
        (TECH_PENCIL, "Карандаш"),
        (TECH_PASTEL, "Пастель"),
        (TECH_OTHER, "Другое"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="works",
        verbose_name="Ученик",
    )
    # Для работ, добавленных администратором в галерею без привязки к пользователю
    author_name = models.CharField("Автор (если без пользователя)", max_length=255, blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="works",
        verbose_name="Курс",
    )
    title = models.CharField("Название", max_length=255)
    image = models.FileField("Картинка", upload_to="works/")
    description = models.TextField("Описание", blank=True)
    technique = models.CharField("Техника", max_length=30, choices=TECHNIQUE_CHOICES, default=TECH_OTHER)
    created_at = models.DateTimeField("Дата", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_comment = models.TextField("Комментарий администратора", blank=True)
    is_visible = models.BooleanField("Показывать в галерее", default=True)

    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"
        ordering = ["-created_at"]

    @property
    def author_display(self) -> str:
        if self.student:
            return (self.student.get_full_name() or self.student.username).strip()
        return self.author_name or "Без автора"

    def __str__(self) -> str:
        return self.title


class News(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True, blank=True)
    short_text = models.CharField("Краткий текст", max_length=400)
    text = models.TextField("Текст")
    image = models.FileField("Картинка", upload_to="news/", blank=True, null=True)
    created_at = models.DateTimeField("Дата", auto_now_add=True)
    is_published = models.BooleanField("Опубликована", default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_ru(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class NewsComment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="comments", verbose_name="Новость")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="news_comments", verbose_name="Пользователь")
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий к новости"
        verbose_name_plural = "Комментарии к новостям"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.user} → {self.news}"


class ApplicationRequest(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_NEW, "Новая"),
        (STATUS_IN_PROGRESS, "В обработке"),
        (STATUS_DONE, "Завершена"),
        (STATUS_CANCELLED, "Отменена"),
    )

    name = models.CharField("Имя", max_length=255)
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Сообщение", blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField("Дата", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Пользователь",
    )
    title = models.CharField("Заголовок", max_length=255)
    text = models.TextField("Текст")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
