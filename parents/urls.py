from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    # ===== PARENT URLs =====
    # Список родителей
    path(
        '',
        views.ParentListView.as_view(),
        name='parent-list'
    ),
    
    # Детали родителя
    path(
        '<int:pk>/',
        views.ParentDetailView.as_view(),
        name='parent-detail'
    ),
    
    # Создание родителя
    path(
        'create/',
        views.ParentCreateView.as_view(),
        name='parent-create'
    ),
    
    # Редактирование родителя
    path(
        '<int:pk>/edit/',
        views.ParentUpdateView.as_view(),
        name='parent-update'
    ),
    
    # Удаление родителя
    path(
        '<int:pk>/delete/',
        views.ParentDeleteView.as_view(),
        name='parent-delete'
    ),
    
    # ===== PARENT-STUDENT RELATION URLs =====
    # Список связей
    path(
        'relations/',
        views.ParentStudentRelationListView.as_view(),
        name='relation-list'
    ),
    
    # Создание связи
    path(
        'relations/create/',
        views.ParentStudentRelationCreateView.as_view(),
        name='relation-create'
    ),
    
    # Редактирование связи
    path(
        'relations/<int:pk>/edit/',
        views.ParentStudentRelationUpdateView.as_view(),
        name='relation-update'
    ),
    
    # Удаление связи
    path(
        'relations/<int:pk>/delete/',
        views.ParentStudentRelationDeleteView.as_view(),
        name='relation-delete'
    ),
]
