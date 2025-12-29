"""
Модели для управления данными о родителях и опекунах студентов.

Включает справочник типов родственных связей, контактную информацию,
адреса проживания и историю взаимодействия родителей с учебным заведением.

Компетенция ПК-1: Создание и управление информационными ресурсами.
Компетенция ПК-7: Разработка бизнес-приложений.
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings


class RelationType(models.Model):
    """
    Справочник типов родственных связей.
    
    Определяет возможные типы отношений между родителем и студентом:
    отец, мать, опекун, брат, сестра и т.д.
    
    Используется для классификации контактов в системе.
    """
    # Название типа связи (например, "Мать", "Опекун")
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Название типа родственной связи"
    )
    # Код типа для программной идентификации
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Код типа (например, MOTHER, FATHER, GUARDIAN)"
    )
    # Описание типа связи
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Описание типа родственной связи"
    )
    # Активен ли тип (для мягкого удаления)
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Активен ли тип связи"
    )
    # Служебные поля для аудита
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Тип родственной связи"
        verbose_name_plural = "Типы родственных связей"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Parent(models.Model):
    """
    Основная таблица данных о родителях и опекунах студентов.
    
    Содержит личную информацию, контактные данные, адреса и другую
    информацию необходимую для коммуникации с семьями студентов.
    
    Компетенция ПК-1: Создание и управление информационными ресурсами.
    """
    # Варианты гендера
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]

    # Статусы родителя (активен, не активен, вышел на пенсию и т.д.)
    STATUS_CHOICES = [
        ('ACTIVE', 'Активный'),
        ('INACTIVE', 'Неактивный'),
        ('DECEASED', 'Скончался'),
    ]
    
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='parent_profile',
    null=True,
    blank=True,
    help_text="Связь с учетной записью пользователя"
    )


    # ===== ЛИЧНАЯ ИНФОРМАЦИЯ =====
    # Имя родителя
    first_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Имя родителя/опекуна"
    )
    # Фамилия родителя
    last_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Фамилия родителя/опекуна"
    )
    # Отчество (опционально)
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Отчество"
    )
    # Дата рождения
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Дата рождения"
    )
    # Гендер
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        help_text="Гендер"
    )
    
    # ===== КОНТАКТНАЯ ИНФОРМАЦИЯ =====
    # Основной email
    email = models.EmailField(
        db_index=True,
        help_text="Основной email"
    )
    # Основной телефон
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Введите корректный номер телефона',
            )
        ],
        help_text="Основной телефон"
    )
    # Дополнительный телефон (рабочий, мобильный и т.д.)
    phone_secondary = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Введите корректный номер телефона',
            )
        ],
        help_text="Дополнительный телефон"
    )
    # Мессенджер (Telegram, WhatsApp и т.д.) и адрес/ID в нём
    messenger = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Мессенджер (Telegram, WhatsApp, Viber и т.д.)"
    )
    # ID/адрес в мессенджере
    messenger_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID или адрес в выбранном мессенджере"
    )
    
    # ===== АДРЕСНАЯ ИНФОРМАЦИЯ =====
    # Страна проживания
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Страна проживания"
    )
    # Город/область
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Город/область"
    )
    # Улица и номер дома
    street_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Улица и номер дома"
    )
    # Почтовый индекс
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Почтовый индекс"
    )
    
    # ===== ПРОФЕССИОНАЛЬНАЯ ИНФОРМАЦИЯ =====
    # Место работы
    employer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Место работы"
    )
    # Должность
    job_position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Должность на месте работы"
    )
    # Рабочий телефон
    work_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Введите корректный номер телефона',
            )
        ],
        help_text="Рабочий телефон"
    )
    
    # ===== СТАТУС И ПРАВА =====
    # Статус родителя
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        db_index=True,
        help_text="Статус родителя"
    )
    # Может ли получать уведомления (отказался или нет)
    can_receive_notifications = models.BooleanField(
        default=True,
        help_text="Может ли получать уведомления"
    )
    # Предпочтительный способ связи (email, phone, messenger)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('PHONE', 'Телефон'),
            ('MESSENGER', 'Мессенджер'),
        ],
        default='EMAIL',
        help_text="Предпочтительный способ связи"
    )
    # Согласие на обработку персональных данных
    consent_gdpr = models.BooleanField(
        default=False,
        help_text="Согласие на обработку персональных данных"
    )
    # Дата согласия
    consent_gdpr_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Дата согласия на обработку данных"
    )
    
    # ===== СЛУЖЕБНЫЕ ПОЛЯ =====
    # Дата регистрации в системе
    registered_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Дата регистрации"
    )
    # Дата последнего обновления информации
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Дата последнего обновления"
    )
    # Дата последней активности (отправка/получение сообщений)
    last_activity = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Дата последней активности"
    )

    class Meta:
        verbose_name = "Родитель/Опекун"
        verbose_name_plural = "Родители/Опекуны"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['status', '-registered_at']),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_full_name(self):
        """Возвращает полное имя родителя."""
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.last_name} {self.first_name}{middle}"

    def get_age(self):
        """Возвращает возраст родителя в годах."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def update_last_activity(self):
        """Обновляет время последней активности."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    @property
    def is_active_parent(self):
        """Активный ли родитель."""
        return self.status == 'ACTIVE'


class ParentStudentRelation(models.Model):
    """
    Связь между родителем и студентом.
    
    Определяет какой родитель опекает какого студента и какой
    тип родственной связи между ними (мать, отец, опекун и т.д.).
    
    Компетенция ПК-1: Создание и управление информационными ресурсами.
    """
    # Родитель/опекун
    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name='student_relations',
        help_text="Родитель/опекун"
    )
    # Студент (внешняя связь - предполагаем наличие модели Student)
    # Поле integer для гибкости (в случае если Student в другом приложении)
    student_id = models.IntegerField(
        db_index=True,
        help_text="ID студента"
    )
    # Тип родственной связи
    relation_type = models.ForeignKey(
        RelationType,
        on_delete=models.PROTECT,
        related_name='parent_relations',
        help_text="Тип родственной связи"
    )
    # Является ли основным контактом (приоритет при отправке уведомлений)
    is_primary_contact = models.BooleanField(
        default=False,
        help_text="Основной контакт для уведомлений"
    )
    # Активна ли связь
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Активна ли связь"
    )
    # Дата начала связи (когда родитель начал опекать студента)
    start_date = models.DateField(
        auto_now_add=True,
        help_text="Дата начала опеки"
    )
    # Дата окончания связи (если опека прекратилась)
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Дата окончания опеки (если применимо)"
    )
    # Служебные поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Связь родителя со студентом"
        verbose_name_plural = "Связи родителей со студентами"
        ordering = ['parent', 'is_primary_contact']
        # Один родитель не может иметь две связи с одним студентом одного типа
        unique_together = [['parent', 'student_id', 'relation_type']]

    def __str__(self):
        return f"{self.parent.get_full_name()} ({self.relation_type.name}) - Студент {self.student_id}"
