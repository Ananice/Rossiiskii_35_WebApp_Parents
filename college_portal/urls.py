"""================================================================================
МОДУЛЬ: college_portal.urls
ОПИСАНИЕ: Маршрутизация (URL configuration) для всего проекта
КОМПЕТЕНЦИИ: ПК-1 (управление информационными ресурсами)
================================================================================

ОПИСАНИЕ МАРШРУТОВ:
  1. /СО НВЕРТУЮЩЕЕ МАРШРУТЫ:
     - GET  /                  → index() - главная страница
     - GET  /login/            → login_view() - вход в систему
     - POST /login/            → login_view() - обработка входа
     - GET  /logout/           → logout_view() - выход из системы
     - GET  /dashboard/        → dashboard() - главный дашборд
     - GET  /messages/         → messages_view() - страница сообщений

  2. API ENDPOINTS:
     - GET  /api/messages/     → api_messages() - получить сообщения
     - POST /api/messages/send/ → api_send_message() - отправить сообщение

  3. АДМИНПАНЕЛЬ:
     - GET  /admin/            → административная панель Django

  4. ОБРАБОТЧИКИ ОШИБОК:
     - 404 Not Found         → page_not_found()
     - 500 Server Error      → server_error()

  5. СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ:
     - /static/     → CSS, JS, изображения
     - /media/      → Пригруженные данные (в разработке)

НОМЕНКЛАТУРА:
  - name (str): Проверенные имена урлов для редиректов в views
  - pattern: Маршрут URL (regex или path-style)
  - view: вид (view function)
  - methods: Поддерживаемые HTTP методы
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views


# ==============================================================================
# ОСНОВНЫЕ МАРШРУТЫ
# ==============================================================================

urlpatterns = [
    # АДМИНПАНЕЛЬ DJANGO
    path('admin/', admin.site.urls),
    
    # ГЛАВНАЯ СТРАНИЦА
    # --------
    # ENDPOINT: GET /
    # DESCRIPTION: Главная страница приложения
    # METHODS: GET
    # RESPONSE: редирект на /dashboard/ (если авторизован) или /login/ (если нет)
    path('', views.index, name='index'),
    
    # АУТЕНТИФИКАЦИЯ
    # --------
    # ENDPOINT: GET/POST /login/
    # DESCRIPTION: Паге входа и обработка тыли утентификации
    # METHODS: GET, POST
    # GET RESPONSE: Не вторні ю щикт Внихатися auth/login.html
    # POST RESPONSE: редирект на /dashboard/ (если ок, или обратно в login.html с ошибкой)
    path('login/', views.login_view, name='login'),
    
    # ENDPOINT: GET /logout/
    # DESCRIPTION: Выход из системы и раздеструкция сессии
    # METHODS: GET
    # RESPONSE: редирект на /login/
    # REQUIRES: Номя авторизован (если нет - редирект на /login/)
    path('logout/', views.logout_view, name='logout'),
    
    # ДАШБОРД
    # --------
    # ENDPOINT: GET /dashboard/
    # DESCRIPTION: Основной дашборд с персонализированным контентом в зависимости от роли
    # METHODS: GET
    # RESPONSE: 
    #   - Лог = 'administrator' → рендер dashboard/admin.html (админ-панель)
    #   - Лог = 'staff' → рендер dashboard/staff.html (дашборд сотрудника)
    #   - Лог = 'parent' → рендер dashboard/parent.html (дашборд родителя)
    # REQUIRES: Номя авторизован (если нет - редирект на /login/)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # МОДУЛЬ СООБЩЕНИЙ
    # --------
    # ENDPOINT: GET /messages/
    # DESCRIPTION: Основная страница со списком контактов с дынамическим подсчётом непрочитанных сообщений
    # METHODS: GET
    # RESPONSE: рендер messages/messages.html с контактами
    # REQUIRES: Номя авторизован
    path('messages/', views.messages_view, name='messages'),
    
    # API ENDPOINTS
    # --------
    # ENDPOINT: GET /api/messages/
    # DESCRIPTION: JSON API для получения сообщений между конкретным пользователями
    # METHODS: GET
    # QUERY PARAMS: contact_id (int) - ID контакта
    # RESPONSE: JSON со списком сообщений или ошибка
    # EXAMPLE: curl "http://localhost:8000/api/messages/?contact_id=5"
    # REQUIRES: Номя авторизован
    path('api/messages/', views.api_messages, name='api_messages'),
    
    # ENDPOINT: POST /api/messages/send/
    # DESCRIPTION: JSON API для отправки нового сообщения
    # METHODS: POST
    # REQUEST BODY (JSON): {"recipient_id": <int>, "content": "<string>"}
    # RESPONSE: JSON с инфо соствленном сообщении
    # EXAMPLE: curl -X POST http://localhost:8000/api/messages/send/ \\
    #             -H "Content-Type: application/json" \\
    #             -d '{"recipient_id": 5, "content": "Hello!"}'
    # REQUIRES: Номя авторизован
    path('api/messages/send/', views.api_send_message, name='api_send_message'),
]

# ==============================================================================
# СТАТИЧЕСКИЕ МЕДИА ФАЙЛЫ (ДЛЯ DEBUG=True)
# ==============================================================================

if settings.DEBUG:
    # Обслуживание статических файлов (КСС, JS)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Обслуживание медиа файлов (пригруженные изображения)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ==============================================================================
# ОБРАБОТЧИКИ ОШИБОК
# ==============================================================================

# 404 - Страница не найдена
handler404 = 'college_portal.views.page_not_found'

# 500 - Ошибка сервера
handler500 = 'college_portal.views.server_error'

# ==============================================================================
# НОМЕНКЛАТУРА ГОТОВЫМ К ПОДКЛЮЧЕНИЮ (РАСКОММЕНТИРОВАТЬ):
# ==============================================================================

# urlpatterns += [path('students/', include('students.urls'))]
# urlpatterns += [path('parents/', include('parents.urls'))]
# urlpatterns += [path('employees/', include('employees.urls'))]
# urlpatterns += [path('communications/', include('communications.urls'))]
# urlpatterns += [path('reports/', include('reports.urls'))]
