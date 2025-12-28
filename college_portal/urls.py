# =====================================================================================
# ФАЙЛ: college_portal/urls.py
# ОПИСАНИЕ: Главный файл маршрутизации для всего проекта
# КОМПЕТЕНЦИИ: ПК-1 (управление информационными ресурсами)
# =====================================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    # АДМИНИСТРИРОВАНИЕ
    path('admin/', admin.site.urls),
    
    # АУТЕНТИФИКАЦИЯ
    # URL: /
    path('', views.index, name='index'),
    
    # URL: /login/
    # МЕТОДЫ: GET (показать форму), POST (обработать вход)
    path('login/', views.login_view, name='login'),
    
    # URL: /logout/
    path('logout/', views.logout_view, name='logout'),
    
    # ДАШБОРДЫ
    # URL: /dashboard/
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # МОДУЛЬ СООБЩЕНИЙ
    # URL: /messages/
    path('messages/', views.messages_view, name='messages'),
    
    # API ENDPOINTS
    # URL: /api/messages/
    path('api/messages/', views.api_messages, name='api_messages'),
    
    # URL: /api/messages/send/
    path('api/messages/send/', views.api_send_message, name='api_send_message'),
]

# ПОДКЛЮЧЕНИЕ URL'ОВ ПРИЛОЖЕНИЙ
# path('students/', include('students.urls')),
# path('parents/', include('parents.urls')),
# path('employees/', include('employees.urls')),
# path('communications/', include('communications.urls')),
# path('reports/', include('reports.urls')),

# ПОДКЛЮЧЕНИЕ СТАТИЧЕСКИХ И МЕДИА ФАЙЛОВ
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ОБРАБОтЧИКИ ОШИБОК
handler404 = 'college_portal.views.page_not_found'
handler500 = 'college_portal.views.server_error'