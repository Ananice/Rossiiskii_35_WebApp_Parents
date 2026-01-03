from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Создаёт демо-пользователей: admin1 / staff1 / parent1"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="Admin12345!",
            help="Пароль для всех демо-аккаунтов (по умолчанию: Admin12345!)",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        password = options["password"]

        demo_users = [
            ("admin1", "admin", True, True),
            ("staff1", "employee", False, False),
            ("parent1", "parent", False, False),
        ]

        for username, role, is_staff, is_superuser in demo_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "role": role,
                    "is_active": True,
                    "is_staff": is_staff,
                    "is_superuser": is_superuser,
                },
            )

            # Если пользователь уже был — всё равно приводим роль/флаги к нужным
            user.role = role
            user.is_active = True
            user.is_staff = is_staff
            user.is_superuser = is_superuser

            # Всегда перезаписываем пароль на демо-пароль
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'CREATED' if created else 'UPDATED'}: {username} (role={role})"
                )
            )

        self.stdout.write(self.style.WARNING(f"Demo password: {password}"))
