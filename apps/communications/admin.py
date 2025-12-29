"""
Communications Admin Configuration
===================================
Конфигурация админ-панели для моделей коммуникации.

Включает:
- User админ с фильтрацией по ролям
- Message админ с поиском
- Report админ со статусами
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Message, Report


# ===== CUSTOM USER ADMIN =====
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Расширенная админ-панель для User модели с поддержкой ролей.
    """
    
    # Поля для отображения в списке
    list_display = (
        'username', 
        'get_full_name', 
        'email', 
        'role',
        'is_active',
        'created_at'
    )
    
    # Фильтры в боковой панели
    list_filter = (
        'role',
        'is_active',
        'created_at',
    )
    
    # Поиск по полям
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'phone',
    )
    
    # Группировка полей в форме
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'password')
        }),
        ('Личные данные', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('Система ролей', {
            'fields': ('role',),
            'description': 'Выберите роль пользователя в системе'
        }),
        ('Статус и права', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    
    # Сортировка по умолчанию
    ordering = ('-created_at',)
    
    def get_full_name(self, obj):
        """Показывает полное имя пользователя"""
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Полное имя'


# ===== MESSAGE ADMIN =====
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Админ-панель для сообщений.
    """
    
    # Поля для отображения в списке
    list_display = (
        'subject',
        'sender',
        'recipient',
        'is_read',
        'created_at',
    )
    
    # Фильтры в боковой панели
    list_filter = (
        'is_read',
        'created_at',
        ('sender', admin.RelatedOnlyFieldListFilter),
        ('recipient', admin.RelatedOnlyFieldListFilter),
    )
    
    # Поиск
    search_fields = (
        'subject',
        'content',
        'sender__username',
        'recipient__username',
    )
    
    # Группировка полей
    fieldsets = (
        ('Основное', {
            'fields': ('sender', 'recipient', 'subject', 'content')
        }),
        ('Вложения', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
        ('Статус чтения', {
            'fields': ('is_read', 'read_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Только для чтения
    readonly_fields = ('created_at', 'updated_at')
    
    # Сортировка
    ordering = ('-created_at',)
    
    # Действия (масовые операции)
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Пометить сообщения как прочитанные"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} сообщений помечено как прочитанные.')
    mark_as_read.short_description = 'Пометить как прочитанные'
    
    def mark_as_unread(self, request, queryset):
        """Пометить сообщения как непрочитанные"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} сообщений помечено как непрочитанные.')
    mark_as_unread.short_description = 'Пометить как непрочитанные'


# ===== REPORT ADMIN =====
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Админ-панель для отчетов.
    """
    
    # Поля для отображения в списке
    list_display = (
        'title',
        'employee',
        'report_type',
        'status',
        'created_at',
    )
    
    # Фильтры в боковой панели
    list_filter = (
        'report_type',
        'status',
        'created_at',
        ('employee', admin.RelatedOnlyFieldListFilter),
    )
    
    # Поиск
    search_fields = (
        'title',
        'content',
        'employee__username',
    )
    
    # Группировка полей
    fieldsets = (
        ('Основное', {
            'fields': ('employee', 'report_type', 'title', 'status')
        }),
        ('Содержимое', {
            'fields': ('content',)
        }),
        ('Вложения', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Только для чтения
    readonly_fields = ('created_at', 'updated_at')
    
    # Сортировка
    ordering = ('-created_at',)
    
    # Действия (масовые операции)
    actions = ['publish_reports', 'archive_reports']
    
    def publish_reports(self, request, queryset):
        """Опубликовать отчеты"""
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} отчетов опубликовано.')
    publish_reports.short_description = 'Опубликовать отчеты'
    
    def archive_reports(self, request, queryset):
        """Отправить отчеты в архив"""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} отчетов отправлено в архив.')
    archive_reports.short_description = 'Отправить в архив'
