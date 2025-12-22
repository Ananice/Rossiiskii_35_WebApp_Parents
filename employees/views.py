"""
Представления (views) для управления сотрудниками.
Реализует все CRUD операции (Create, Read, Update, Delete) с фильтрацией и поиском.

Компетенция ПК-1: Способность создавать, редактировать и наполнять контентом информационные ресурсы.
ПК-7: Способность разрабатывать бизнес-приложения, используя высокоуровневые методы программирования.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Employee, Department, Position, Qualification, EmployeeSchedule
from .forms import (
    EmployeeForm, EmployeeFilterForm, DepartmentForm, 
    PositionForm, QualificationForm, EmployeeScheduleForm
)


class EmployeeListView(LoginRequiredMixin, ListView):
    """
    Представление для вывода списка всех сотрудников с фильтрацией и поиском.
    Требует аутентификации. Поддерживает фильтрацию по отделу и должности.
    """
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    queryset = Employee.objects.select_related('position', 'department').prefetch_related('qualifications')

    def get_queryset(self):
        """
        Получить queryset с фильтрацией по поисковому запросу и фильтрам.
        """
        queryset = super().get_queryset()
        
        # Поиск по ФИО, email, ID сотрудника
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(last_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(employee_id__icontains=search_query)
            )
        
        # Фильтр по отделу
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Фильтр по должности
        position_id = self.request.GET.get('position')
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        
        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Фильтр по активным контактам
        is_contact = self.request.GET.get('is_contact')
        if is_contact == 'true':
            queryset = queryset.filter(is_contact_person=True, status='ACTIVE')
        
        return queryset.order_by('department', 'last_name')

    def get_context_data(self, **kwargs):
        """
        Добавить в контекст фильтры и поисковый запрос.
        """
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        context['positions'] = Position.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        context['filter_form'] = EmployeeFilterForm(self.request.GET)
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для просмотра полной информации о сотруднике.
    Включает данные по должности, отделу и квалификациям.
    """
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'
    queryset = Employee.objects.select_related('position', 'department').prefetch_related('qualifications')

    def get_context_data(self, **kwargs):
        """
        Добавить в контекст расписание и дополнительные данные.
        """
        context = super().get_context_data(**kwargs)
        try:
            context['schedule'] = self.object.schedule
        except EmployeeSchedule.DoesNotExist:
            context['schedule'] = None
        
        context['years_of_service'] = self.object.get_years_of_service()
        context['age'] = self.object.get_age()
        context['is_available'] = self.object.is_available_for_communication()
        return context


class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Представление для создания новой записи о сотруднике.
    Требует специального разрешения (permission).
    """
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    permission_required = 'employees.add_employee'
    success_url = reverse_lazy('employees:employee_list')

    def form_valid(self, form):
        """
        Обработать успешную отправку формы с логированием.
        """
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Сотрудник {form.instance.get_full_name()} успешно добавлен."
        )
        return response

    def get_context_data(self, **kwargs):
        """
        Добавить заголовок и подсказку для формы создания.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление нового сотрудника'
        context['action'] = 'create'
        return context


class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Представление для редактирования информации о сотруднике.
    Требует специального разрешения.
    """
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    permission_required = 'employees.change_employee'
    success_url = reverse_lazy('employees:employee_list')

    def form_valid(self, form):
        """
        Обработать успешное обновление с логированием.
        """
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Информация о сотруднике {form.instance.get_full_name()} обновлена."
        )
        return response

    def get_context_data(self, **kwargs):
        """
        Добавить информацию о редактировании.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.get_full_name()}'
        context['action'] = 'update'
        return context


class EmployeeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Представление для удаления записи о сотруднике.
    Требует специального разрешения. На практике используется soft-delete.
    """
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    permission_required = 'employees.delete_employee'
    success_url = reverse_lazy('employees:employee_list')

    def delete(self, request, *args, **kwargs):
        """
        Переопределить удаление на изменение статуса на 'DISMISSED'.
        """
        self.object = self.get_object()
        self.object.status = 'DISMISSED'
        self.object.save()
        messages.success(
            request,
            f"Сотрудник {self.object.get_full_name()} помечен как уволенный."
        )
        return redirect(self.success_url)


class DepartmentListView(LoginRequiredMixin, ListView):
    """
    Представление для вывода списка отделов с иерархией.
    """
    model = Department
    template_name = 'employees/department_list.html'
    context_object_name = 'departments'
    paginate_by = 15
    queryset = Department.objects.filter(is_active=True).select_related('head_of_department', 'parent_department')

    def get_context_data(self, **kwargs):
        """
        Добавить статистику по отделам.
        """
        context = super().get_context_data(**kwargs)
        context['departments_count'] = Department.objects.filter(is_active=True).count()
        context['departments_with_employees'] = Department.objects.annotate(
            employee_count=Count('employees')
        ).filter(is_active=True, employee_count__gt=0)
        return context


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для просмотра отдела со всеми его сотрудниками.
    """
    model = Department
    template_name = 'employees/department_detail.html'
    context_object_name = 'department'
    queryset = Department.objects.select_related('head_of_department', 'parent_department')

    def get_context_data(self, **kwargs):
        """
        Добавить сотрудников отдела и подразделения.
        """
        context = super().get_context_data(**kwargs)
        context['employees'] = self.object.employees.filter(status='ACTIVE')
        context['subdepartments'] = self.object.subdepartments.filter(is_active=True)
        return context


class PositionListView(LoginRequiredMixin, ListView):
    """
    Представление для вывода списка должностей.
    """
    model = Position
    template_name = 'employees/position_list.html'
    context_object_name = 'positions'
    paginate_by = 20
    queryset = Position.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        """
        Добавить статистику по должностям.
        """
        context = super().get_context_data(**kwargs)
        context['positions_count'] = Position.objects.filter(is_active=True).count()
        context['positions_with_employees'] = Position.objects.annotate(
            employee_count=Count('employees')
        ).filter(is_active=True, employee_count__gt=0)
        return context


@login_required
def contact_persons_list(request):
    """
    Специальное представление для вывода только активных контактных лиц.
    Используется в системе коммуникаций для отправки уведомлений родителям.
    """
    contact_persons = Employee.objects.filter(
        is_contact_person=True,
        status='ACTIVE',
        can_send_notifications=True
    ).select_related('position', 'department').order_by('department', 'last_name')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        contact_persons = contact_persons.filter(
            Q(last_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )
    
    # Фильтр по отделу
    department_id = request.GET.get('department')
    if department_id:
        contact_persons = contact_persons.filter(department_id=department_id)
    
    paginator = Paginator(contact_persons, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'contact_persons': page_obj.object_list,
        'search_query': search_query,
        'departments': Department.objects.filter(is_active=True),
        'total_count': paginator.count,
    }
    
    return render(request, 'employees/contact_persons_list.html', context)


@login_required
def employee_schedule_view(request, pk):
    """
    Представление для просмотра расписания сотрудника.
    Показывает рабочие часы и время консультаций с родителями.
    """
    employee = get_object_or_404(Employee, pk=pk)
    try:
        schedule = employee.schedule
    except EmployeeSchedule.DoesNotExist:
        schedule = None
    
    context = {
        'employee': employee,
        'schedule': schedule,
    }
    
    return render(request, 'employees/employee_schedule.html', context)


@login_required
def api_get_employee_by_id(request):
    """
    API эндпоинт для получения информации о сотруднике по ID (JSON).
    Используется фронтенд-компонентами для асинхронной загрузки данных.
    """
    employee_id = request.GET.get('id')
    if not employee_id:
        return JsonResponse({'error': 'ID не указан'}, status=400)
    
    try:
        employee = Employee.objects.get(employee_id=employee_id, status='ACTIVE')
        return JsonResponse({
            'id': employee.id,
            'employee_id': employee.employee_id,
            'full_name': employee.get_full_name(),
            'position': employee.position.name,
            'department': employee.department.name,
            'email': employee.email,
            'phone': employee.phone,
            'is_contact_person': employee.is_contact_person,
        })
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Сотрудник не найден'}, status=404)


@login_required
def export_employees_list(request):
    """
    Экспорт списка сотрудников в CSV для аналитики и отчётности.
    """
    import csv
    from datetime import datetime
    
    employees = Employee.objects.filter(status='ACTIVE').select_related(
        'position', 'department'
    ).values_list(
        'employee_id', 'last_name', 'first_name', 'position__name',
        'department__name', 'email', 'phone', 'hire_date'
    )
    
    response = HttpResponseForbidden() if not request.user.has_perm('employees.view_employee') else None
    if response:
        return response
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="employees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Табельный №', 'Фамилия', 'Имя', 'Должность', 'Отдел', 'Email', 'Телефон', 'Дата найма'])
    
    for employee in employees:
        writer.writerow(employee)
    
    return response
