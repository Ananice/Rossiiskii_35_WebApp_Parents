"""
Команда Django для создания групп пользователей и назначения прав доступа.

Компетенция ПК-1: Создание и управление информационными ресурсами.
Компетенция ПК-7: Разработка бизнес-приложений.

Создаёт 3 основные группы:
1. Администраторы - полный доступ ко всем функциям
2. Сотрудники - управление сообщениями, отчетами, просмотр пользователей
3. Родители - просмотр своих сообщений и отчетов о детях

Использование:
    python manage.py create_groups
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from communications.models import User, Message, Report


class Command(BaseCommand):
    """
    Management команда для инициализации системы групп и прав доступа.
    """
    help = 'Создаёт группы пользователей и назначает права доступа (RBAC)'

    def handle(self, *args, **options):
        """
        Основной метод команды. Создаёт 3 группы с соответствующими правами.
        """

        # ═════════════════════════════════════════════════════════════
        # 1️⃣ ГРУППА: АДМИНИСТРАТОРЫ
        # ═════════════════════════════════════════════════════════════
        
        admins_group, created = Group.objects.get_or_create(name='Администраторы')
        
        # Получаем ContentType для моделей
        user_content_type = ContentType.objects.get_for_model(User)
        message_content_type = ContentType.objects.get_for_model(Message)
        report_content_type = ContentType.objects.get_for_model(Report)

        # Администраторы получают ВСЕ права на эти модели
        admin_permissions = Permission.objects.filter(
            content_type__in=[user_content_type, message_content_type, report_content_type]
        )
        
        admins_group.permissions.set(admin_permissions)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Группа "Администраторы" создана с полными правами')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Группа "Администраторы" уже существует, права обновлены')
            )

        # ═════════════════════════════════════════════════════════════
        # 2️⃣ ГРУППА: СОТРУДНИКИ
        # ═════════════════════════════════════════════════════════════
        
        staff_group, created = Group.objects.get_or_create(name='Сотрудники')
        
        # Сотрудники могут:
        # - Отправлять и редактировать свои сообщения
        # - Просматривать сообщения
        # - Создавать и редактировать отчеты
        # - Просматривать пользователей (для адресации сообщений)
        staff_permissions = Permission.objects.filter(
            codename__in=[
                'add_message',      # Отправлять сообщения
                'change_message',   # Редактировать свои сообщения
                'view_message',     # Просматривать сообщения
                'add_report',       # Создавать отчеты
                'change_report',    # Редактировать отчеты
                'view_report',      # Просматривать отчеты
                'view_user',        # Просматривать пользователей
            ]
        )
        
        staff_group.permissions.set(staff_permissions)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Группа "Сотрудники" создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Группа "Сотрудники" уже существует, права обновлены')
            )

        # ═════════════════════════════════════════════════════════════
        # 3️⃣ ГРУППА: РОДИТЕЛИ
        # ═════════════════════════════════════════════════════════════
        
        parents_group, created = Group.objects.get_or_create(name='Родители')
        
        # Родители могут:
        # - Просматривать свои сообщения и отчеты о своих детях
        # - Отправлять ответы на сообщения от сотрудников
        parent_permissions = Permission.objects.filter(
            codename__in=[
                'view_message',     # Просматривать свои сообщения
                'add_message',      # Отправлять ответы
                'view_report',      # Просматривать отчеты о своих детях
            ]
        )
        
        parents_group.permissions.set(parent_permissions)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Группа "Родители" создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Группа "Родители" уже существует, права обновлены')
            )

        # ═════════════════════════════════════════════════════════════
        # ✅ ИТОГ
        # ═════════════════════════════════════════════════════════════
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ ВСЕ ГРУППЫ УСПЕШНО СОЗДАНЫ!\n'
                '   Администраторы:  Полный доступ\n'
                '   Сотрудники:      Управление сообщениями и отчетами\n'
                '   Родители:        Просмотр своих данных и ответы\n'
            )
        )
