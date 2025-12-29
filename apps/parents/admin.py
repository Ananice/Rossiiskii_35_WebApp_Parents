"""
Admin-панель для управления родителями и опекунами студентов.

Включает интерфейсы для управления:
- Типы родственных связей (справочник)
- Данные о родителях (личная информация, контакты, адреса)
- Связи между родителями и студентами

Компетенция ПК-1: Создание и управление информационными ресурсами.
Компетенция ПК-7: Разработка бизнес-приложений.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import RelationType, Parent, ParentStudentRelation


@admin.register(RelationType)
class RelationTypeAdmin(admin.ModelAdmin):
    """Admin для справочника типов родственных связей."""
    
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'code')
        }),
        ('Описание', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Аудит', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    """Admin для управления данными о родителях/опекунах."""
    
    list_display = (
        'get_full_name',
        'email',
        'phone',
        'get_status_badge',
        'registered_at'
    )
    list_filter = ('status', 'registered_at', 'gender', 'can_receive_notifications')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('registered_at', 'updated_at', 'last_activity')
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender')
        }),
        ('Контактная информация', {
            'fields': (
                'email',
                'phone',
                'phone_secondary',
                'messenger',
                'messenger_id',
                'preferred_contact_method'
            )
        }),
        ('Адрес проживания', {
            'fields': ('country', 'city', 'street_address', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Информация о работе', {
            'fields': ('employer', 'job_position', 'work_phone'),
            'classes': ('collapse',)
        }),
        ('Статус и права', {
            'fields': (
                'status',
                'can_receive_notifications',
                'consent_gdpr',
                'consent_gdpr_date'
            )
        }),
        ('Служебная информация', {
            'fields': ('registered_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_badge(self, obj):
        """Возвращает статус с цветным индикатором."""
        colors = {
            'ACTIVE': '#28a745',
            'INACTIVE': '#ffc107',
            'DECEASED': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Статус'
    
    def get_full_name(self, obj):
        """Возвращает полное имя для списка."""
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'
    
    actions = ['mark_active', 'mark_inactive']
    
    def mark_active(self, request, queryset):
        """Действие для активации родителей."""
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} родителей активированы.')
    mark_active.short_description = 'Активировать выбранных родителей'
    
    def mark_inactive(self, request, queryset):
        """Действие для деактивации родителей."""
        updated = queryset.update(status='INACTIVE')
        self.message_user(request, f'{updated} родителей деактивированы.')
    mark_inactive.short_description = 'Деактивировать выбранных родителей'


@admin.register(ParentStudentRelation)
class ParentStudentRelationAdmin(admin.ModelAdmin):
    """Admin для связей между родителями и студентами."""
    
    list_display = (
        'get_parent_name',
        'student_id',
        'relation_type',
        'is_primary_contact',
        'is_active',
        'start_date'
    )
    list_filter = (
        'is_primary_contact',
        'is_active',
        'relation_type',
        'start_date'
    )
    search_fields = (
        'parent__first_name',
        'parent__last_name',
        'student_id'
    )
    readonly_fields = ('start_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Связь', {
            'fields': ('parent', 'student_id', 'relation_type')
        }),
        ('Статус', {
            'fields': ('is_primary_contact', 'is_active')
        }),
        ('Даты', {
            'fields': ('start_date', 'end_date'),
        }),
        ('Аудит', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_parent_name(self, obj):
        """Возвращает ФИО родителя."""
        return obj.parent.get_full_name()
    get_parent_name.short_description = 'Родитель'
    
    actions = ['mark_primary_contact', 'mark_active_relations', 'mark_inactive_relations']
    
    def mark_primary_contact(self, request, queryset):
        """Действие для установки как основного контакта."""
        updated = queryset.update(is_primary_contact=True)
        self.message_user(request, f'{updated} отношений установлены как основной контакт.')
    mark_primary_contact.short_description = 'Установить как основной контакт'
    
    def mark_active_relations(self, request, queryset):
        """Действие для активации отношений."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} отношений активированы.')
    mark_active_relations.short_description = 'Активировать отношения'
    
    def mark_inactive_relations(self, request, queryset):
        """Действие для деактивации отношений."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} отношений деактивированы.')
    mark_inactive_relations.short_description = 'Деактивировать отношения'
