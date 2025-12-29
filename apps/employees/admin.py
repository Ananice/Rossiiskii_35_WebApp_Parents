"""
Настройка админ-панели Django для управления сотрудниками, отделениями и должностями.
Обеспечивает быстрые фильтры, поиск, былк-операции и чтение-онли поля.

Компетенция ПК-1.1: Проведение работ по созданию, редактированию и контролю выгружки контента.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Department, Position, Qualification, Employee, EmployeeSchedule


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Админ для отделений.
    """
    list_display = [
        'code',
        'name',
        'parent_department',
        'get_head_name',
        'get_employee_count',
        'get_status_badge',
        'created_at',
    ]
    list_filter = [
        'is_active',
        ('parent_department', admin.RelatedOnlyFieldListFilter),
        'created_at',
    ]
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            _('Основная информация'),
            {'fields': ('name', 'code', 'parent_department')}
        ),
        (
            _('Контактная информация'),
            {'fields': ('email', 'phone', 'office_location')}
        ),
        (
            _('Руководство'),
            {'fields': ('head_of_department',)}
        ),
        (
            _('Описание'),
            {'fields': ('description',)}
        ),
        (
            _('Статус'),
            {'fields': ('is_active',)}
        ),
        (
            _('Метаданные'),
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}
        ),
    )
    ordering = ['code']

    def get_head_name(self, obj):
        """Отображает имя руководителя отделения."""
        return obj.head_of_department.get_full_name() if obj.head_of_department else 'Не назначен'
    get_head_name.short_description = _('Руководитель')

    def get_employee_count(self, obj):
        """Количество сотрудников в отделении."""
        count = obj.employees.count()
        return format_html(
            '<span style="background-color: #0066cc; color: white; padding: 3px 10px; '
            'border-radius: 4px;">{}</span>',
            count
        )
    get_employee_count.short_description = _('Сотрудников')

    def get_status_badge(self, obj):
        """Бейдж статуса активности."""
        color = '#28a745' if obj.is_active else '#dc3545'
        text = 'Активно' if obj.is_active else 'Неактивно'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px;">{}</span>',
            color,
            text
        )
    get_status_badge.short_description = _('Статус')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """
    Админ для должностей.
    """
    list_display = [
        'code',
        'name',
        'level',
        'department_category',
        'required_experience_years',
        'get_salary_range',
        'get_employee_count',
        'get_status_badge',
    ]
    list_filter = [
        'level',
        'department_category',
        'is_active',
        'required_experience_years',
    ]
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            _('Основная информация'),
            {'fields': ('name', 'code', 'level', 'department_category')}
        ),
        (
            _('Требования'),
            {
                'fields': (
                    'required_education',
                    'required_experience_years',
                )
            }
        ),
        (
            _('ОП и ЗП'),
            {'fields': ('salary_range_min', 'salary_range_max')}
        ),
        (
            _('Описание'),
            {'fields': ('description',)}
        ),
        (
            _('Статус'),
            {'fields': ('is_active',)}
        ),
        (
            _('Метаданные'),
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}
        ),
    )
    ordering = ['level', 'name']

    def get_salary_range(self, obj):
        """Показывает ранг зарплаты."""
        if obj.salary_range_min and obj.salary_range_max:
            return f"{obj.salary_range_min} - {obj.salary_range_max} руб."
        return 'Не указана'
    get_salary_range.short_description = _('Диапазон ЗП')

    def get_employee_count(self, obj):
        """Количество сотрудников на данной должности."""
        count = obj.employees.count()
        return format_html(
            '<span style="background-color: #0066cc; color: white; padding: 3px 10px; '
            'border-radius: 4px;">{}</span>',
            count
        )
    get_employee_count.short_description = _('Сотрудников')

    def get_status_badge(self, obj):
        """Бейдж активности."""
        color = '#28a745' if obj.is_active else '#dc3545'
        text = 'Активна' if obj.is_active else 'Неактивна'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px;">{}</span>',
            color,
            text
        )
    get_status_badge.short_description = _('Статус')


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    """
    Админ для квалификаций.
    """
    list_display = ['code', 'name', 'type', 'issuing_organization', 'is_mandatory', 'get_status_badge']
    list_filter = ['type', 'is_mandatory', 'is_active']
    search_fields = ['name', 'code', 'issuing_organization']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            _('Основная информация'),
            {'fields': ('name', 'code', 'type')}
        ),
        (
            _('Тип квалификации'),
            {'fields': ('issuing_organization',)}
        ),
        (
            _('Условия'),
            {'fields': ('is_mandatory',)}
        ),
        (
            _('Описание'),
            {'fields': ('description',)}
        ),
        (
            _('Статус'),
            {'fields': ('is_active',)}
        ),
        (
            _('Метаданные'),
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}
        ),
    )
    ordering = ['type', 'name']

    def get_status_badge(self, obj):
        """Бейдж статуса активности."""
        color = '#28a745' if obj.is_active else '#dc3545'
        text = 'Активна' if obj.is_active else 'Неактивна'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px;">{}</span>',
            color,
            text
        )
    get_status_badge.short_description = _('Статус')


class EmployeeScheduleInline(admin.TabularInline):
    """
    Внутристрочные расписания для редактирования прямо таблице сотрудника.
    """
    model = EmployeeSchedule
    extra = 0
    fields = [
        'monday_start',
        'monday_end',
        'tuesday_start',
        'tuesday_end',
        'friday_start',
        'friday_end',
        'consultation_hours',
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Комплексный админ для сотрудников с всеми деталями.
    """
    list_display = [
        'get_employee_id',
        'get_full_name',
        'position',
        'department',
        'email',
        'status',
        'is_contact_person',
        'hire_date',
        'created_at',
    ]
    list_filter = [
        'status',
        'is_contact_person',
        'can_send_notifications',
        'department',
        'position',
        'hire_date',
        'created_at',
    ]
    search_fields = [
        'last_name',
        'first_name',
        'middle_name',
        'employee_id',
        'email',
        'phone',
    ]
    readonly_fields = ['hire_date', 'created_at', 'updated_at', 'get_years_of_service']
    inlines = [EmployeeScheduleInline]

    fieldsets = (
        (
            _('Личные данные'),
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'middle_name',
                    'date_of_birth',
                    'gender',
                    'photo',
                )
            }
        ),
        (
            _('Контактная информация'),
            {
                'fields': (
                    'email',
                    'phone',
                    'mobile_phone',
                )
            }
        ),
        (
            _('Профессиональные данные'),
            {
                'fields': (
                    'employee_id',
                    'position',
                    'department',
                    'qualifications',
                    'office_room',
                    'biography',
                )
            }
        ),
        (
            _('Данные о работе'),
            {
                'fields': (
                    'status',
                    'hire_date',
                    'termination_date',
                    'get_years_of_service',
                )
            }
        ),
        (
            _('Права и доступ'),
            {
                'fields': (
                    'is_contact_person',
                    'can_send_notifications',
                )
            }
        ),
        (
            _('Метаданные'),
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),
            }
        ),
    )
    filter_horizontal = ['qualifications']
    ordering = ['last_name', 'first_name']
    date_hierarchy = 'hire_date'

    def get_employee_id(self, obj):
        """Табельный номер."""
        return format_html(
            '<strong>{}</strong>',
            obj.employee_id
        )
    get_employee_id.short_description = _('Табельный №')

    def get_full_name(self, obj):
        """Полное имя сотрудника."""
        return obj.get_full_name()
    get_full_name.short_description = _('ФИО')

    def get_readonly_fields(self, request, obj=None):
        """
        Сделать некоторые поля только для чтения после сохранения.
        """
        if obj:  # При редактировании
            return self.readonly_fields + ['employee_id']
        return self.readonly_fields


@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    """
    Админ для расписания сотрудников.
    """
    list_display = ['employee', 'get_consultation_info', 'created_at']
    search_fields = ['employee__last_name', 'employee__first_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            _('Основная информация'),
            {'fields': ('employee',)}
        ),
        (
            _('Пн-Чт'),
            {
                'fields': (
                    'monday_start',
                    'monday_end',
                    'tuesday_start',
                    'tuesday_end',
                    'wednesday_start',
                    'wednesday_end',
                    'thursday_start',
                    'thursday_end',
                )
            }
        ),
        (
            _('Пт-Сб'),
            {
                'fields': (
                    'friday_start',
                    'friday_end',
                    'saturday_start',
                    'saturday_end',
                )
            }
        ),
        (
            _('Вс'),
            {'fields': ('sunday_start', 'sunday_end')}
        ),
        (
            _('Консультации с родителями'),
            {'fields': ('consultation_hours',)}
        ),
        (
            _('Метаданные'),
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),
            }
        ),
    )
    ordering = ['employee']

    def get_consultation_info(self, obj):
        """Ниформация о времени консультаций."""
        return obj.consultation_hours or 'Не указаны'
    get_consultation_info.short_description = _('Время консультаций')
