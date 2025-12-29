"""
Модель данных для управления сотрудниками учебного заведения.
Включает справочники должностей, отделений, структуру сотрудников с их контактными данными,
квалификационными подтверждениями и историей работы.

Компетенция ПК-1: Способность создавать, редактировать и наполнять контентом 
информационные ресурсы предприятия.
"""

from django.db import models
from django.core.validators import RegexValidator, URLValidator
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class Department(models.Model):
    """
    Справочник отделений/факультетов учебного заведения.
    Иерархическая структура позволяет отражать подразделения и их филиалы.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Полное название отделения/факультета"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Код отделения (например, ИС-01)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Описание функций и ответственности отделения"
    )
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subdepartments',
        help_text="Родительское отделение (для иерархии)"
    )
    head_of_department = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        help_text="Руководитель отделения"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email отделения для координации"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Введите корректный номер телефона',
            )
        ],
        help_text="Телефон отделения"
    )
    office_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Местоположение офиса"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Активно ли отделение"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Отделение"
        verbose_name_plural = "Отделения"
        ordering = ['code', 'name']
        unique_together = [['code', 'name']]
        indexes = [
            models.Index(fields=['code', '-is_active']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Position(models.Model):
    """
    Справочник должностей в учебном заведении.
    Содержит иерархию должностей с указанием уровня компетенции требуемой для каждой.
    """
    LEVEL_CHOICES = [
        (1, 'Стажер'),
        (2, 'Специалист'),
        (3, 'Старший специалист'),
        (4, 'Руководитель'),
        (5, 'Директор'),
    ]

    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Название должности"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Код должности (например, TEACH-001)"
    )
    department_category = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Категория (Педагогический, Административный, Технический)"
    )
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        help_text="Уровень ответственности"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Описание обязанностей и требований"
    )
    required_education = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Требуемое образование"
    )
    required_experience_years = models.IntegerField(
        default=0,
        help_text="Требуемый опыт работы в годах"
    )
    salary_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Минимальная зарплата"
    )
    salary_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Максимальная зарплата"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Активна ли должность"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        ordering = ['level', 'name']
        indexes = [
            models.Index(fields=['code', '-is_active']),
            models.Index(fields=['department_category', 'level']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Qualification(models.Model):
    """
    Справочник квалификаций, сертификатов и специальных навыков.
    Связывает сотрудников с их профессиональными достижениями.
    """
    QUALIFICATION_TYPE_CHOICES = [
        ('DEGREE', 'Учёная степень'),
        ('CERTIFICATE', 'Сертификат'),
        ('COURSE', 'Курс повышения квалификации'),
        ('LICENSE', 'Лицензия'),
        ('SKILL', 'Профессиональный навык'),
    ]

    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Название квалификации"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Код квалификации"
    )
    type = models.CharField(
        max_length=20,
        choices=QUALIFICATION_TYPE_CHOICES,
        db_index=True,
        help_text="Тип квалификации"
    )
    issuing_organization = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Организация-издатель"
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    is_mandatory = models.BooleanField(
        default=False,
        help_text="Обязательна ли для определённых должностей"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Квалификация"
        verbose_name_plural = "Квалификации"
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Employee(models.Model):
    """
    Основная таблица данных о сотрудниках учебного заведения.
    Содержит личную информацию, должность, отделение и статус работы.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Активный'),
        ('ON_LEAVE', 'В отпуске'),
        ('SUSPENDED', 'Приостановлен'),
        ('DISMISSED', 'Уволен'),
    ]

    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]

    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='employee_profile',
    null=True,
    blank=True,
    help_text="Связь с учетной записью пользователя"
    )

    # Личная информация
    first_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Имя сотрудника"
    )
    last_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Фамилия сотрудника"
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Отчество"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Дата рождения"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        help_text="Пол"
    )
    
    # Контактная информация
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="Корпоративный email"
    )
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
    mobile_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Введите корректный номер телефона',
            )
        ],
        help_text="Мобильный телефон"
    )
    
    # Профессиональная информация
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Табельный номер"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name='employees',
        help_text="Должность"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='employees',
        help_text="Отделение"
    )
    qualifications = models.ManyToManyField(
        Qualification,
        related_name='employees',
        blank=True,
        help_text="Квалификации и сертификаты"
    )
    
    # Статус работы
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        db_index=True,
        help_text="Статус сотрудника"
    )
    hire_date = models.DateField(
        auto_now_add=True,
        help_text="Дата найма"
    )
    termination_date = models.DateField(
        blank=True,
        null=True,
        help_text="Дата увольнения"
    )
    
    # Дополнительная информация
    office_room = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Номер кабинета/офиса"
    )
    photo = models.ImageField(
        upload_to='employee_photos/',
        blank=True,
        null=True,
        help_text="Фотография сотрудника"
    )
    biography = models.TextField(
        blank=True,
        null=True,
        help_text="Биография и достижения"
    )
    
    # Служебная информация
    is_contact_person = models.BooleanField(
        default=False,
        help_text="Может ли быть контактным лицом для родителей"
    )
    can_send_notifications = models.BooleanField(
        default=True,
        help_text="Может ли отправлять уведомления родителям"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['employee_id', '-status']),
            models.Index(fields=['email']),
            models.Index(fields=['position', 'status']),
            models.Index(fields=['department', '-hire_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(hire_date__lte=timezone.now().date()),
                name='hire_date_not_future'
            )
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.employee_id})"

    def get_full_name(self):
        """Возвращает полное имя сотрудника."""
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.last_name} {self.first_name}{middle}"

    def get_age(self):
        """Возвращает возраст сотрудника в годах."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def is_available_for_communication(self):
        """Проверяет, доступен ли сотрудник для общения с родителями."""
        return self.status == 'ACTIVE' and self.is_contact_person

    def get_years_of_service(self):
        """Возвращает стаж работы в годах."""
        end_date = self.termination_date if self.termination_date else timezone.now().date()
        return (end_date - self.hire_date).days // 365

    @property
    def is_active_employee(self):
        """Активный ли сотрудник."""
        return self.status == 'ACTIVE'


class EmployeeSchedule(models.Model):
    """
    Расписание рабочего графика сотрудников.
    Позволяет планировать доступность для встреч и консультаций с родителями.
    """
    DAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='schedule',
        help_text="Сотрудник"
    )
    monday_start = models.TimeField(default='09:00', help_text="Начало работы в пн")
    monday_end = models.TimeField(default='18:00', help_text="Конец работы в пн")
    tuesday_start = models.TimeField(default='09:00')
    tuesday_end = models.TimeField(default='18:00')
    wednesday_start = models.TimeField(default='09:00')
    wednesday_end = models.TimeField(default='18:00')
    thursday_start = models.TimeField(default='09:00')
    thursday_end = models.TimeField(default='18:00')
    friday_start = models.TimeField(default='09:00')
    friday_end = models.TimeField(default='18:00')
    saturday_start = models.TimeField(default='10:00', blank=True, null=True)
    saturday_end = models.TimeField(default='14:00', blank=True, null=True)
    sunday_start = models.TimeField(blank=True, null=True)
    sunday_end = models.TimeField(blank=True, null=True)
    
    consultation_hours = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Время консультаций с родителями (например, пн-чт 16:00-18:00)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Расписание сотрудника"
        verbose_name_plural = "Расписания сотрудников"

    def __str__(self):
        return f"Расписание {self.employee.get_full_name()}"
