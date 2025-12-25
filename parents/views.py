"""
Views для CRUD операций с родителями и связями.

Включает:
- ParentListView - список всех родителей с поиском и фильтрацией
- ParentDetailView - детали конкретного родителя
- ParentCreateView - создание нового родителя
- ParentUpdateView - редактирование родителя
- ParentDeleteView - удаление родителя
- ParentStudentRelationListView - список связей
- ParentStudentRelationCreateView - создание связи
- ParentStudentRelationUpdateView - редактирование связи
- ParentStudentRelationDeleteView - удаление связи

Компетенция ПК-1: Создание и управление информационными ресурсами.
Компетенция ПК-7: Разработка бизнес-приложений.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .models import Parent, ParentStudentRelation, RelationType
from .forms import ParentForm, ParentStudentRelationForm, RelationTypeForm


# ===== PARENT VIEWS =====

class ParentListView(LoginRequiredMixin, ListView):
    """
    Список всех родителей с поиском и фильтрацией.
    
    Фильтры:
    - по статусу (активные, неактивные, скончались)
    - по способу получения уведомлений
    - по гендеру
    
    Поиск:
    - по ФИО
    - по email
    - по телефону
    """
    model = Parent
    template_name = 'parents/parent_list.html'
    context_object_name = 'parents'
    paginate_by = 20
    
    def get_queryset(self):
        """Получает queryset с фильтрацией и поиском."""
        queryset = Parent.objects.all().order_by('-registered_at')
        
        # Поиск по ФИО, email, телефону
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Фильтр по статусу
        status = self.request.GET.get('status', '').strip()
        if status and status in ['ACTIVE', 'INACTIVE', 'DECEASED']:
            queryset = queryset.filter(status=status)
        
        # Фильтр по согласию на уведомления
        notifications = self.request.GET.get('notifications', '').strip()
        if notifications == 'yes':
            queryset = queryset.filter(can_receive_notifications=True)
        elif notifications == 'no':
            queryset = queryset.filter(can_receive_notifications=False)
        
        # Фильтр по гендеру
        gender = self.request.GET.get('gender', '').strip()
        if gender and gender in ['M', 'F']:
            queryset = queryset.filter(gender=gender)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет дополнительный контекст для фильтров."""
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['notifications'] = self.request.GET.get('notifications', '')
        context['gender'] = self.request.GET.get('gender', '')
        context['statuses'] = Parent._meta.get_field('status').choices
        return context


class ParentDetailView(LoginRequiredMixin, DetailView):
    """
    Детали конкретного родителя.
    
    Показывает:
    - Личную информацию
    - Контактные данные
    - Адрес
    - Информацию о работе
    - Связанные студенты
    - Историю взаимодействия (если доступна)
    """
    model = Parent
    template_name = 'parents/parent_detail.html'
    context_object_name = 'parent'
    
    def get_context_data(self, **kwargs):
        """Добавляет связанные студенты и дополнительный контекст."""
        context = super().get_context_data(**kwargs)
        context['student_relations'] = self.object.student_relations.filter(
            is_active=True
        ).select_related('relation_type')
        return context


class ParentCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового родителя.
    
    Требует:
    - Имя и фамилия
    - Email (уникальный)
    - Телефон (валидный)
    
    Опционально:
    - Отчество
    - Дата рождения
    - Адрес
    - Информация о работе
    """
    model = Parent
    form_class = ParentForm
    template_name = 'parents/parent_form.html'
    success_url = reverse_lazy('parents:parent-list')
    
    def form_valid(self, form):
        """Сохраняет родителя и добавляет сообщение об успехе."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Родитель {form.instance.get_full_name()} успешно создан!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание нового родителя'
        context['button_text'] = 'Создать'
        return context


class ParentUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование данных родителя.
    
    Позволяет изменить любую информацию о родителе.
    """
    model = Parent
    form_class = ParentForm
    template_name = 'parents/parent_form.html'
    success_url = reverse_lazy('parents:parent-list')
    
    def form_valid(self, form):
        """Сохраняет изменения и добавляет сообщение об успехе."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Данные родителя {form.instance.get_full_name()} обновлены!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.get_full_name()}'
        context['button_text'] = 'Обновить'
        return context


class ParentDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление родителя (мягкое удаление - изменение статуса).
    
    Вместо удаления устанавливает статус 'INACTIVE'.
    """
    model = Parent
    template_name = 'parents/parent_confirm_delete.html'
    success_url = reverse_lazy('parents:parent-list')
    
    def delete(self, request, *args, **kwargs):
        """Вместо удаления деактивирует родителя."""
        self.object = self.get_object()
        parent_name = self.object.get_full_name()
        self.object.status = 'INACTIVE'
        self.object.save()
        messages.success(
            request,
            f'Родитель {parent_name} деактивирован.'
        )
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        """Добавляет информацию в контекст удаления."""
        context = super().get_context_data(**kwargs)
        context['parent'] = self.object
        return context


# ===== PARENT-STUDENT RELATION VIEWS =====

class ParentStudentRelationListView(LoginRequiredMixin, ListView):
    """
    Список всех связей между родителями и студентами.
    
    Показывает:
    - Родителя (ФИО)
    - Студента (ID)
    - Тип связи
    - Статус (активна/неактивна)
    - Основной контакт
    """
    model = ParentStudentRelation
    template_name = 'parents/relation_list.html'
    context_object_name = 'relations'
    paginate_by = 20
    
    def get_queryset(self):
        """Получает queryset с поиском и фильтрацией."""
        queryset = ParentStudentRelation.objects.all().select_related(
            'parent', 'relation_type'
        ).order_by('-start_date')
        
        # Поиск по ФИО родителя или ID студента
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(parent__first_name__icontains=search) |
                Q(parent__last_name__icontains=search) |
                Q(student_id__icontains=search)
            )
        
        # Фильтр по активности
        is_active = self.request.GET.get('is_active', '').strip()
        if is_active == 'yes':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'no':
            queryset = queryset.filter(is_active=False)
        
        # Фильтр по типу связи
        relation_type = self.request.GET.get('relation_type', '').strip()
        if relation_type:
            queryset = queryset.filter(relation_type_id=relation_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет дополнительный контекст для фильтров."""
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['is_active'] = self.request.GET.get('is_active', '')
        context['relation_types'] = RelationType.objects.filter(is_active=True)
        return context


class ParentStudentRelationCreateView(LoginRequiredMixin, CreateView):
    """
    Создание новой связи между родителем и студентом.
    
    Требует:
    - Выбор родителя
    - ID студента
    - Тип связи
    
    Опционально:
    - Дата окончания
    """
    model = ParentStudentRelation
    form_class = ParentStudentRelationForm
    template_name = 'parents/relation_form.html'
    success_url = reverse_lazy('parents:relation-list')
    
    def form_valid(self, form):
        """Сохраняет связь и добавляет сообщение об успехе."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Связь создана: {form.instance.parent.get_full_name()} '
            f'({form.instance.relation_type.name}) - студент {form.instance.student_id}'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание связи'
        context['button_text'] = 'Создать'
        return context


class ParentStudentRelationUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование связи между родителем и студентом."""
    model = ParentStudentRelation
    form_class = ParentStudentRelationForm
    template_name = 'parents/relation_form.html'
    success_url = reverse_lazy('parents:relation-list')
    
    def form_valid(self, form):
        """Сохраняет изменения и добавляет сообщение об успехе."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Связь успешно обновлена!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование связи'
        context['button_text'] = 'Обновить'
        return context


class ParentStudentRelationDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление связи между родителем и студентом."""
    model = ParentStudentRelation
    template_name = 'parents/relation_confirm_delete.html'
    success_url = reverse_lazy('parents:relation-list')
    
    def delete(self, request, *args, **kwargs):
        """Удаляет связь с сообщением об успехе."""
        self.object = self.get_object()
        parent_name = self.object.parent.get_full_name()
        messages.success(
            request,
            f'Связь {parent_name} - студент {self.object.student_id} удалена.'
        )
        return super().delete(request, *args, **kwargs)
