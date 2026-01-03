# Веб-приложение взаимодействия сотрудников с родителями

**Тема ВКР:** Разработка веб-приложения взаимодействия сотрудников колледжа  
с родителями обучающихся (на примере ЧОУВО "Московский университет имени С.Ю. Витте")

**Студент:** Российский Даниил Ильич  
**Направление:** Бизнес-информатика, профиль "Цифровая экономика"  
**Период (практика):** Декабрь 2025

## Описание проекта
Веб-приложение предназначено для оптимизации взаимодействия между сотрудниками учебного заведения
и родителями студентов.

## Функциональность (MVP практики)
- Аутентификация пользователей (3 роли: администратор, сотрудник, родитель).
- Личный кабинет / дашборд в зависимости от роли.
- Обмен сообщениями между сотрудниками и родителями (страница + API).

## Технологический стек
- Backend: Python + Django 5, Django REST Framework, PostgreSQL.
- Frontend: Django templates (HTML/CSS/JS), Bootstrap (через crispy-bootstrap5).
- База данных: PostgreSQL (подключение через psycopg2).
- Конфигурация: переменные окружения (.env) через python-dotenv.

### Планируется на этап ВКР
- Docker-окружение для развёртывания (docker-compose и т.п.).

## Установка и запуск (Windows / PowerShell)
1. Клонировать репозиторий и перейти в папку проекта:
   ```powershell
   git clone https://github.com/Ananice/Rossiiskii_35_WebApp_Parents.git
   cd Rossiiskii_35_WebApp_Parents
   ```

2. Создать виртуальное окружение и установить зависимости:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Создать файл окружения .env на основе .env.example:
- Скопировать `.env.example` -> `.env`
- Указать параметры PostgreSQL `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- Указать `DJANGO_SECRET_KEY`

4. Применить миграции:
   ```powershell
   python manage.py migrate
   ```

5. Создать демо-аккаунты: admin1, staff1, parent1
   ```powershell
   python manage.py create_demo_users
   ```
- Демо-аккаунты: `admin1`, `staff1`, `parent1`
- Пароль: `Admin12345!`

6. Запустить сервер:
   ```powershell
   python manage.py runserver
   ```

После запуска приложение доступно по адресу: http://127.0.0.1:8000/

## Основные URL (для проверки)
- `/login/` — вход в систему
- `/dashboard/` — дашборд (контент зависит от роли)
- `/messages/` — сообщения
- `/api/messages/?contact_id=<id>` — получить сообщения (GET)
- `/api/messages/send/` — отправить сообщение (POST)

## Проверка подключения PostgreSQL
В Django shell можно проверить активный драйвер:
   ```powershell
   python manage.py shell
   ```
   ```python
   from django.db import connection
   connection.vendor  # ожидается 'postgresql'
   ```