from django.core.management.base import BaseCommand
from apps.communications.models import User, Message
from apps.public.models import Feedback


class Command(BaseCommand):
    help = 'Заполнить БД демонстрационными данными'

    def handle(self, *args, **kwargs):

        # --- Сообщения между parent1 и staff1 ---
        try:
            parent = User.objects.get(username='parent1')
            staff = User.objects.get(username='staff1')

            msgs = [
                (parent, staff, 'Вопрос об успеваемости',
                 'Добрый день! Подскажите, как обстоят дела с успеваемостью моего сына в этом семестре?'),
                (staff, parent, 'Re: Вопрос об успеваемости',
                 'Здравствуйте! Успеваемость на хорошем уровне. По математике — 4, по информатике — 5. Замечаний нет.'),
                (parent, staff, 'Re: Вопрос об успеваемости',
                 'Большое спасибо за информацию! Буду следить за его успехами.'),
                (staff, parent, 'Уведомление о собрании',
                 'Уважаемый родитель! Приглашаем вас на родительское собрание 25 марта в 18:00.'),
                (parent, staff, 'Re: Уведомление о собрании',
                 'Спасибо, обязательно приду!'),
            ]

            for sender, recipient, subject, content in msgs:
                Message.objects.get_or_create(
                    sender=sender,
                    recipient=recipient,
                    subject=subject,
                    defaults={'content': content}
                )
            self.stdout.write(self.style.SUCCESS('✓ Сообщения созданы'))
        except User.DoesNotExist as e:
            self.stdout.write(self.style.WARNING(f'Пользователь не найден: {e}'))

        # --- Обращения родителей ---
        feedbacks = [
            ('Петрова Анна Ивановна', 'petrova@mail.ru', '+7 916 123-45-67',
             'Вопрос о расписании', 'Здравствуйте! Когда будет опубликовано расписание на следующий семестр?'),
            ('Сидоров Олег Петрович', 'sidorov@gmail.com', '+7 925 987-65-43',
             'Пропуски занятий', 'Мой сын пропустил несколько занятий по болезни. Как оформить справку?'),
            ('Козлова Татьяна Михайловна', 'kozlova@yandex.ru', '+7 903 555-11-22',
             'Благодарность преподавателю', 'Хочу выразить благодарность классному руководителю за внимательное отношение к детям.'),
        ]

        for name, email, phone, subject, message in feedbacks:
            Feedback.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'phone': phone,
                    'subject': subject,
                    'message': message,
                    'consent_pd': True,
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Обращения созданы'))

        self.stdout.write(self.style.SUCCESS('\n=== Демо-данные загружены ==='))
