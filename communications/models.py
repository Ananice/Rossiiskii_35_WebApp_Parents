"""
Communications Models
=====================
Модели для системы взаимодействия сотрудников колледжа с родителями.

Структура:
- User: Базовая модель пользователя с ролями (admin, employee, parent, student)
- Message: Сообщения между пользователями
- Report: Отчеты о студентах (успеваемость, поведение, пропуски)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


# ===== USER MODEL (Расширенная) =====
class User(AbstractUser):
    """
    Расширенная модель пользователя с поддержкой ролей.
    
    Роли:
    - admin: Администратор системы
    - employee: Сотрудник (преподаватель, куратор, декан)
    - parent: Родитель/опекун студента
    - student: Студент
    """
    
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('employee', 'Сотрудник'),
        ('parent', 'Родитель'),
        ('student', 'Студент'),
    ]
    
    # Основные поля модели
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student',
        help_text='Роль пользователя в системе'
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text='Телефон контакта'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        help_text='Аватар пользователя'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Активен ли пользователь в системе'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Дата создания профиля'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Дата последнего обновления'
    )
    
    def __str__(self):
        """Строковое представление пользователя"""
        full_name = self.get_full_name() or self.username
        return f"{full_name} ({self.get_role_display()})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['role', 'is_active']),
        ]


# ===== MESSAGE MODEL =====
class Message(models.Model):
    """
    Модель сообщений между пользователями.
    
    Используется для:
    - Сообщений от сотрудника к родителю
    - Ответов от родителя к сотруднику
    - Оповещений системы
    """
    
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        help_text='Отправитель сообщения'
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        help_text='Получатель сообщения'
    )
    subject = models.CharField(
        max_length=200,
        help_text='Тема сообщения'
    )
    content = models.TextField(
        help_text='Содержимое сообщения'
    )
    attachment = models.FileField(
        upload_to='message_attachments/', 
        blank=True, 
        null=True,
        help_text='Вложение к сообщению (если есть)'
    )
    is_read = models.BooleanField(
        default=False,
        help_text='Прочитано ли сообщение'
    )
    read_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text='Время прочтения сообщения'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Время отправления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Время последнего изменения'
    )
    
    def __str__(self):
        """Строковое представление сообщения"""
        return f"{self.sender.username} → {self.recipient.username}: {self.subject[:30]}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]


# ===== REPORT MODEL =====
class Report(models.Model):
    """
    Модель отчетов сотрудников о студентах.
    
    Используется для:
    - Отчетов об успеваемости
    - Отчетов о поведении
    - Отчетов о пропусках
    - Прочих замечаний и информации
    """
    
    REPORT_TYPE_CHOICES = [
        ('progress', 'Успеваемость'),
        ('behavior', 'Поведение'),
        ('absence', 'Пропуски'),
        ('discipline', 'Дисциплина'),
        ('achievement', 'Достижения'),
        ('other', 'Другое'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('archived', 'В архиве'),
    ]
    
    # Связи
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_reports',
        limit_choices_to={'role': 'employee'},
        help_text='Сотрудник, создавший отчет'
    )
    # TODO: Добавить связь на модель Student (когда она будет создана)
    # student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='reports')
    
    # Основные поля
    report_type = models.CharField(
        max_length=20, 
        choices=REPORT_TYPE_CHOICES,
        help_text='Тип отчета'
    )
    title = models.CharField(
        max_length=200,
        help_text='Заголовок отчета'
    )
    content = models.TextField(
        help_text='Содержимое отчета'
    )
    attachment = models.FileField(
        upload_to='report_attachments/', 
        blank=True, 
        null=True,
        help_text='Документы или доказательства'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Статус отчета'
    )
    
    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Дата создания отчета'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Дата последнего изменения'
    )
    published_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text='Дата публикации отчета'
    )
    
    def __str__(self):
        """Строковое представление отчета"""
        return f"{self.title} ({self.get_report_type_display()})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['created_at']),
        ]

