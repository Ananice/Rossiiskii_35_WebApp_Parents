"""================================================================================
МОДУЛЬ: apps.core.urls
ОПИСАНИЕ: Маршрутизация (URL configuration) для базового приложения (Core)
КОМПЕТЕНЦИИ: ПК-1 (управление информационными ресурсами)
================================================================================

РОЛЬ МОДУЛЯ В АРХИТЕКТУРЕ:
- Приложение apps.core содержит базовые представления проекта (общие страницы и API).
- Подключается в корневом URLconf проекта через include('apps.core.urls').

ОПИСАНИЕ МАРШРУТОВ:
1. ОСНОВНЫЕ МАРШРУТЫ:
   - GET / → index() - главная страница
   - GET/POST /login/ → login_view() - вход в систему
   - GET /logout/ → logout_view() - выход из системы
   - GET /dashboard/ → dashboard() - главный дашборд
   - GET /messages/ → messages_view() - страница сообщений

2. API ENDPOINTS:
   - GET /api/messages/ → api_messages() - получить сообщения
   - POST /api/messages/send/ → api_send_message() - отправить сообщение

НОМЕНКЛАТУРА:
- app_name (str): Namespace приложения для reverse() и шаблонов
- name (str): Имя маршрута для reverse() и ссылок в шаблонах
- pattern: Маршрут URL (path-style)
- view: Представление (view function)
- methods: Поддерживаемые HTTP методы
"""

from django.urls import path

from . import views


# ==============================================================================
# ПРОСТРАНСТВО ИМЁН ПРИЛОЖЕНИЯ
# ==============================================================================
# Используется для обращения к урлам вида: "core:login", "core:dashboard" и т.д.
app_name = "core"


# ==============================================================================
# ОСНОВНЫЕ МАРШРУТЫ
# ==============================================================================

urlpatterns = [
    # ГЛАВНАЯ СТРАНИЦА
    # --------
    # ENDPOINT: GET /
    # DESCRIPTION: Главная страница приложения
    # METHODS: GET
    # RESPONSE: редирект на /dashboard/ (если авторизован) или /login/ (если нет)
    path("", views.index, name="index"),

    # АУТЕНТИФИКАЦИЯ
    # --------
    # ENDPOINT: GET/POST /login/
    # DESCRIPTION: Страница входа и обработка формы аутентификации
    # METHODS: GET, POST
    # GET RESPONSE: Рендер шаблона auth/login.html
    # POST RESPONSE: редирект на /dashboard/ (если ок, или обратно в login.html с ошибкой)
    path("login/", views.login_view, name="login"),

    # ENDPOINT: GET /logout/
    # DESCRIPTION: Выход из системы и разрушение сессии
    # METHODS: GET
    # RESPONSE: редирект на /login/
    # REQUIRES: Должен быть авторизован (если нет - редирект на /login/)
    path("logout/", views.logout_view, name="logout"),

    # ДАШБОРД
    # --------
    # ENDPOINT: GET /dashboard/
    # DESCRIPTION: Основной дашборд с персонализированным контентом в зависимости от роли
    # METHODS: GET
    # RESPONSE:
    #   - Роль = 'administrator' → рендер dashboard/admin.html (админ-панель)
    #   - Роль = 'staff' → рендер dashboard/staff.html (дашборд сотрудника)
    #   - Роль = 'parent' → рендер dashboard/parent.html (дашборд родителя)
    # REQUIRES: Должен быть авторизован (если нет - редирект на /login/)
    path("dashboard/", views.dashboard, name="dashboard"),

    # МОДУЛЬ СООБЩЕНИЙ
    # --------
    # ENDPOINT: GET /messages/
    # DESCRIPTION: Основная страница со списком контактов с динамическим подсчётом непрочитанных сообщений
    # METHODS: GET
    # RESPONSE: рендер messages/messages.html с контактами
    # REQUIRES: Должен быть авторизован
    path("messages/", views.messages_view, name="messages"),

    # API ENDPOINTS
    # --------
    # ENDPOINT: GET /api/messages/
    # DESCRIPTION: JSON API для получения сообщений между конкретным пользователем
    # METHODS: GET
    # QUERY PARAMS: contact_id (int) - ID контакта
    # RESPONSE: JSON со списком сообщений или ошибка
    # EXAMPLE: curl "http://localhost:8000/api/messages/?contact_id=5"
    # REQUIRES: Должен быть авторизован
    path("api/messages/", views.api_messages, name="api_messages"),

    # ENDPOINT: POST /api/messages/send/
    # DESCRIPTION: JSON API для отправки нового сообщения
    # METHODS: POST
    # REQUEST BODY (JSON): {"recipient_id": <int>, "content": "<string>"}
    # RESPONSE: JSON с инфо о созданном сообщении
    # EXAMPLE: curl -X POST http://localhost:8000/api/messages/send/ \
    #               -H "Content-Type: application/json" \
    #               -d '{"recipient_id": 5, "content": "Hello!"}'
    # REQUIRES: Должен быть авторизован
    path("api/messages/send/", views.api_send_message, name="api_send_message"),
]
