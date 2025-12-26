"""
Communications URLs
===================
URL маршруты для приложения communications (пользователи, сообщения, отчеты).

Namespace: 'communications'

Маршруты:

USER URLs:
- 'user-list' → /communications/users/
- 'user-detail' → /communications/users/<id>/
- 'user-create' → /communications/users/create/
- 'user-update' → /communications/users/<id>/edit/

MESSAGE URLs:
- 'message-list' → /communications/messages/
- 'message-detail' → /communications/messages/<id>/
- 'message-create' → /communications/messages/create/

REPORT URLs:
- 'report-list' → /communications/reports/
- 'report-detail' → /communications/reports/<id>/
- 'report-create' → /communications/reports/create/
- 'report-update' → /communications/reports/<id>/edit/
- 'report-delete' → /communications/reports/<id>/delete/

Компетенция ПК-1: Создание и управление информационными ресурсами.
Компетенция ПК-7: Разработка бизнес-приложений.
"""

from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # ===== USER URLs =====
    # Список пользователей с фильтрацией
    path(
        'users/',
        views.UserListView.as_view(),
        name='user-list'
    ),
    
    # Профиль пользователя
    path(
        'users/<int:pk>/',
        views.UserDetailView.as_view(),
        name='user-detail'
    ),
    
    # Создание нового пользователя (только администратор)
    path(
        'users/create/',
        views.UserCreateView.as_view(),
        name='user-create'
    ),
    
    # Редактирование профиля пользователя
    path(
        'users/<int:pk>/edit/',
        views.UserUpdateView.as_view(),
        name='user-update'
    ),
    
    # ===== MESSAGE URLs =====
    # Список входящих сообщений
    path(
        'messages/',
        views.MessageListView.as_view(),
        name='message-list'
    ),
    
    # Просмотр одного сообщения
    path(
        'messages/<int:pk>/',
        views.MessageDetailView.as_view(),
        name='message-detail'
    ),
    
    # Создание и отправка сообщения
    path(
        'messages/create/',
        views.MessageCreateView.as_view(),
        name='message-create'
    ),
    
    # ===== REPORT URLs =====
    # Список отчетов с фильтрацией
    path(
        'reports/',
        views.ReportListView.as_view(),
        name='report-list'
    ),
    
    # Просмотр одного отчета
    path(
        'reports/<int:pk>/',
        views.ReportDetailView.as_view(),
        name='report-detail'
    ),
    
    # Создание отчета
    path(
        'reports/create/',
        views.ReportCreateView.as_view(),
        name='report-create'
    ),
    
    # Редактирование отчета
    path(
        'reports/<int:pk>/edit/',
        views.ReportUpdateView.as_view(),
        name='report-update'
    ),
    
    # Удаление отчета
    path(
        'reports/<int:pk>/delete/',
        views.ReportDeleteView.as_view(),
        name='report-delete'
    ),
]
