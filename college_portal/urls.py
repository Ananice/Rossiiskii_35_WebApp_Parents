from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from communications import views as comm_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', comm_views.index, name='index'),
    path('login/', comm_views.login_view, name='login'),
    path('logout/', comm_views.logout_view, name='logout'),
    path('dashboard/', comm_views.dashboard, name='dashboard'),
    path('messages/', comm_views.messages_view, name='messages'),
    
    # App URLs
    path('communications/', include('communications.urls')),
    path('parents/', include('parents.urls')),
    path('employees/', include('employees.urls')),
    path('students/', include('students.urls')),
    path('reports/', include('reports.urls')),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
