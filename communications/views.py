"""
Communications Views
====================
Views для моделей User, Message, Report.

Включает:
- UserListView - список пользователей с фильтром по ролям
- UserDetailView - профиль пользователя
- UserCreateView - создание пользователя
- UserUpdateView - редактирование профиля

- MessageListView - входящие сообщения
- MessageCreateView - создание и отправка сообщения
- MessageDetailView - просмотр сообщения

- ReportListView - список отчетов с фильтрацией
- ReportCreateView - создание отчета
- ReportDetailView - просмотр отчета
- ReportUpdateView - редактирование отчета
- ReportDeleteView - удаление отчета

Компетенция ПК-1: Создание и управление информационными ресурсами.
Компетенция ПК-7: Разработка бизнес-приложений.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import User, Message, Report
from .forms import CustomUserCreationForm, UserEditForm, MessageForm, ReportForm


# ===== USER VIEWS =====

class UserListView(LoginRequiredMixin, ListView):
    """
    Список всех пользователей с фильтром по ролям.
    
    Фильтры:
    - по ролям (admin, employee, parent, student)
    - по статусу активности
    - поиск по ФИО, username, email
    """
    model = User
    template_name = 'communications/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        """Получает queryset с фильтрацией и поиском"""
        queryset = User.objects.all().order_by('-created_at')
        
        # Поиск по ФИО, username, email
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Фильтр по ролям
        role = self.request.GET.get('role', '').strip()
        if role and role in [r[0] for r in User.ROLE_CHOICES]:
            queryset = queryset.filter(role=role)
        
        # Фильтр по статусу активности
        is_active = self.request.GET.get('is_active', '').strip()
        if is_active == 'yes':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'no':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет параметры фильтра в контекст"""
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['role'] = self.request.GET.get('role', '')
        context['is_active'] = self.request.GET.get('is_active', '')
        context['roles'] = User.ROLE_CHOICES
        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    """
    Профиль пользователя (свой или других).
    
    Показывает:
    - Личную информацию
    - Контактные данные
    - Роль
    - Статистику (количество сообщений, отчетов)
    """
    model = User
    template_name = 'communications/user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        """Добавляет дополнительную информацию"""
        context = super().get_context_data(**kwargs)
        user = self.object
        
        if user.role == 'employee':
            context['sent_messages'] = Message.objects.filter(sender=user).count()
            context['created_reports'] = Report.objects.filter(employee=user).count()
        elif user.role == 'parent':
            context['received_messages'] = Message.objects.filter(recipient=user).count()
        
        return context


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Создание нового пользователя (только администратор).
    
    Требует роль при создании.
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'communications/user_form.html'
    success_url = reverse_lazy('communications:user-list')
    
    def test_func(self):
        """Проверяет, что это администратор"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        """Сохраняет пользователя и добавляет сообщение"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Пользователь {form.instance.get_full_name()} успешно создан!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание нового пользователя'
        context['button_text'] = 'Создать'
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование профиля пользователя.
    
    Пользователь может редактировать свой профиль,
    администратор - любой профиль.
    """
    model = User
    form_class = UserEditForm
    template_name = 'communications/user_form.html'
    success_url = reverse_lazy('communications:user-list')
    
    def form_valid(self, form):
        """Сохраняет изменения и добавляет сообщение"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Профиль {form.instance.get_full_name()} обновлен!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы"""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.get_full_name()}'
        context['button_text'] = 'Обновить'
        return context


# ===== MESSAGE VIEWS =====

class MessageListView(LoginRequiredMixin, ListView):
    """
    Список входящих сообщений для текущего пользователя.
    
    Фильтры:
    - все сообщения
    - непрочитанные
    - прочитанные
    - поиск по теме
    """
    template_name = 'communications/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        """Получает входящие сообщения для текущего пользователя"""
        queryset = Message.objects.filter(
            recipient=self.request.user
        ).select_related('sender').order_by('-created_at')
        
        # Фильтр по статусу чтения
        filter_type = self.request.GET.get('filter_type', 'all').strip()
        if filter_type == 'unread':
            queryset = queryset.filter(is_read=False)
        elif filter_type == 'read':
            queryset = queryset.filter(is_read=True)
        
        # Поиск по теме и содержимому
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(content__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет параметры фильтра"""
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['filter_type'] = self.request.GET.get('filter_type', 'all')
        context['unread_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context


class MessageDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр одного сообщения.
    
    Автоматически отмечает как прочитанное.
    """
    model = Message
    template_name = 'communications/message_detail.html'
    context_object_name = 'message'
    
    def get(self, request, *args, **kwargs):
        """Отмечает сообщение как прочитанное"""
        response = super().get(request, *args, **kwargs)
        
        message = self.object
        if message.recipient == request.user and not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        
        return response


class MessageCreateView(LoginRequiredMixin, CreateView):
    """
    Создание и отправка нового сообщения.
    
    Отправитель устанавливается автоматически (текущий пользователь).
    """
    model = Message
    form_class = MessageForm
    template_name = 'communications/message_form.html'
    success_url = reverse_lazy('communications:message-list')
    
    def get_form_kwargs(self):
        """Передает текущего пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Устанавливает отправителя и сохраняет"""
        form.instance.sender = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Сообщение отправлено {form.instance.recipient.get_full_name()}!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание сообщения'
        context['button_text'] = 'Отправить'
        return context


# ===== REPORT VIEWS =====

class ReportListView(LoginRequiredMixin, ListView):
    """
    Список отчетов с фильтрацией по типам и статусам.
    
    Фильтры:
    - по типам отчетов
    - по статусам (черновик, опубликовано, архив)
    - поиск по названию
    
    Только сотрудники видят/создают отчеты.
    """
    model = Report
    template_name = 'communications/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        """Получает отчеты созданные текущим пользователем"""
        queryset = Report.objects.filter(
            employee=self.request.user
        ).order_by('-created_at')
        
        # Фильтр по типам отчетов
        report_types = self.request.GET.getlist('report_type')
        if report_types:
            queryset = queryset.filter(report_type__in=report_types)
        
        # Фильтр по статусам
        statuses = self.request.GET.getlist('status')
        if statuses:
            queryset = queryset.filter(status__in=statuses)
        
        # Поиск по названию
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет параметры фильтра"""
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['report_types'] = Report.REPORT_TYPE_CHOICES
        context['statuses'] = Report.STATUS_CHOICES
        return context


class ReportCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового отчета.
    
    Автор (employee) устанавливается автоматически.
    """
    model = Report
    form_class = ReportForm
    template_name = 'communications/report_form.html'
    success_url = reverse_lazy('communications:report-list')
    
    def form_valid(self, form):
        """Устанавливает автора отчета"""
        form.instance.employee = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Отчет "{form.instance.title}" создан!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание отчета'
        context['button_text'] = 'Создать'
        return context


class ReportDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр полной информации об отчете.
    """
    model = Report
    template_name = 'communications/report_detail.html'
    context_object_name = 'report'


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование отчета (только автор или администратор).
    """
    model = Report
    form_class = ReportForm
    template_name = 'communications/report_form.html'
    success_url = reverse_lazy('communications:report-list')
    
    def form_valid(self, form):
        """Сохраняет изменения и добавляет сообщение"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Отчет "{form.instance.title}" обновлен!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет заголовок формы"""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.title}'
        context['button_text'] = 'Обновить'
        return context


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление отчета (только автор или администратор).
    """
    model = Report
    template_name = 'communications/report_confirm_delete.html'
    success_url = reverse_lazy('communications:report-list')
    
    def delete(self, request, *args, **kwargs):
        """Удаляет отчет с сообщением"""
        self.object = self.get_object()
        report_title = self.object.title
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f'Отчет "{report_title}" удален!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Добавляет информацию в контекст удаления"""
        context = super().get_context_data(**kwargs)
        context['report'] = self.object
        return context
