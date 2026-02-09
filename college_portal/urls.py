"""================================================================================
МОДУЛЬ: college_portal.urls
ОПИСАНИЕ: Маршрутизация (URL configuration) для всего проекта
КОМПЕТЕНЦИИ: ПК-1 (управление информационными ресурсами)
================================================================================

ОПИСАНИЕ МАРШРУТОВ:
1. ОСНОВНЫЕ МАРШРУТЫ:
   - GET / → index() - главная страница
   - GET /login/ → login_view() - вход в систему
   - POST /login/ → login_view() - обработка входа
   - GET /logout/ → logout_view() - выход из системы
   - GET /dashboard/ → dashboard() - главный дашборд
   - GET /messages/ → messages_view() - страница сообщений

2. API ENDPOINTS:
   - GET /api/messages/ → api_messages() - получить сообщения
   - POST /api/messages/send/ → api_send_message() - отправить сообщение

3. АДМИНПАНЕЛЬ:
   - GET /admin/ → административная панель Django

4. ОБРАБОТЧИКИ ОШИБОК:
   - 404 Not Found → page_not_found()
   - 500 Server Error → server_error()

5. СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ:
   - /static/ → CSS, JS, изображения
   - /media/ → Загруженные данные (в разработке)

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



# ==============================================================================
# ОСНОВНЫЕ МАРШРУТЫ
# ==============================================================================
#
# ВАЖНО:
# - После рефакторинга проектный модуль college_portal НЕ хранит представления (views).
# - Все пользовательские маршруты вынесены в приложение apps.core и подключаются через include().
#
# ПРЕИМУЩЕСТВА:
# - Разделение ответственности (project urls = “шлюз”, app urls = “бизнес-логика”).
# - Упрощение поддержки и расширения маршрутов.
#

urlpatterns = [
    # АДМИНПАНЕЛЬ DJANGO
    # --------
    # ENDPOINT: GET /admin/
    # DESCRIPTION: Административная панель Django
    # METHODS: GET
    path("admin/", admin.site.urls),
    
    path("", include("apps.public.urls")),
    # МАРШРУТЫ ПРИЛОЖЕНИЯ (CORE)
    # --------
    # ENDPOINTS:
    #   - GET / → index()
    #   - GET/POST /login/ → login_view()
    #   - GET /logout/ → logout_view()
    #   - GET /dashboard/ → dashboard()
    #   - GET /messages/ → messages_view()
    #   - GET /api/messages/ → api_messages()
    #   - POST /api/messages/send/ → api_send_message()
    # DESCRIPTION: Подключение маршрутов приложения apps.core
    # NOTE: Детальная маршрутизация находится в apps/core/urls.py
    path("", include("apps.core.urls")),
]


# ==============================================================================
# СТАТИЧЕСКИЕ МЕДИА ФАЙЛЫ (ДЛЯ DEBUG=True)
# ==============================================================================

if settings.DEBUG:
    # Обслуживание статических файлов (CSS, JS)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Обслуживание медиа файлов (загруженные изображения)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ==============================================================================
# ОБРАБОТЧИКИ ОШИБОК
# ==============================================================================

# 404 - Страница не найдена
handler404 = 'apps.core.views.page_not_found'

# 500 - Ошибка сервера
handler500 = 'apps.core.views.server_error'

# ==============================================================================
# НОМЕНКЛАТУРА ГОТОВЫМ К ПОДКЛЮЧЕНИЮ (РАСКОММЕНТИРОВАТЬ):
# ==============================================================================

# urlpatterns += [path('students/', include('students.urls'))]
# urlpatterns += [path('parents/', include('parents.urls'))]
# urlpatterns += [path('employees/', include('employees.urls'))]
# urlpatterns += [path('communications/', include('communications.urls'))]
# urlpatterns += [path('reports/', include('reports.urls'))]
