from django.db import models
from django.utils import timezone


class Feedback(models.Model):
    STATUS_NEW = "new"
    STATUS_PROCESSED = "processed"
    STATUS_CHOICES = [
        (STATUS_NEW, "Новое"),
        (STATUS_PROCESSED, "Обработано"),
    ]

    public_id = models.CharField("Номер обращения", max_length=32, unique=True, blank=True)

    name = models.CharField("ФИО", max_length=255)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=32)
    subject = models.CharField("Тема", max_length=255)
    message = models.TextField("Текст обращения")
    consent_pd = models.BooleanField("Согласие на обработку ПДн", default=False)

    file_name = models.CharField("Имя файла", max_length=255, blank=True)
    file_content_type = models.CharField("Content-Type", max_length=100, blank=True)
    file_size = models.PositiveIntegerField("Размер (байт)", null=True, blank=True)
    file_data = models.BinaryField("Файл (данные)", null=True, blank=True)

    status = models.CharField("Статус", max_length=16, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and not self.public_id:
            self.public_id = f"FB-{self.created_at.year}-{self.pk:06d}"
            super().save(update_fields=["public_id"])


class News(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    summary = models.TextField("Кратко", blank=True)
    body = models.TextField("Текст", blank=True)
    published_at = models.DateTimeField("Дата", default=timezone.now)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
