# ===================== ИМПОРТЫ =====================
from django.contrib import admin
from django.urls import path, include  # include = подключить urls из приложений
from django.conf import settings
from django.conf.urls.static import static

# ===================== ГЛАВНЫЕ МАРШРУТЫ =====================
urlpatterns = [
    # Admin панель Django (/admin/)
    path('admin/', admin.site.urls),
    
    # Все маршруты приложения college_portal
    # Так что /login/, /dashboard/ и т.д. будут работать
    path('', include('college_portal.urls')),
]

# ===================== STATIC И MEDIA ФАЙЛЫ =====================
# Для разработки: подключить CSS, JS, картинки

if settings.DEBUG:
    # Статические файлы (CSS, JS)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Медиа файлы (загруженные пользователями)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
