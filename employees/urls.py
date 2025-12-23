"""
URL маршруты для модуля управления сотрудниками.

Определяет все доступные эндпоинты для работы с сотрудниками,
отделениями, должностями и расписаниями. Включает CRUD операции,
фильтрацию, поиск, экспорт данных и API эндпоинты для интеграции
с другими модулями системы.

Компетенция ПК-7: Разработка бизнес-приложений.
Компетенция ПК-9: Разработка веб-приложений.
"""

from django.urls import path
from . import views

# Пространство имён для URL маршрутов (используется в шаблонах как {% url 'employees:employee_list' %})
app_name = 'employees'

urlpatterns = [
    # ===== СОТРУДНИКИ - ОСНОВНЫЕ ОПЕРАЦИИ =====
    # Получить список всех сотрудников с фильтрацией и поиском
    # URL: /employees/
    # Метод: GET
    # Permissions: login_required
    path(
        'employees/',
        views.EmployeeListView.as_view(),
        name='employee_list'
    ),
    
    # Получить детальную информацию о конкретном сотруднике
    # URL: /employees/<id>/
    # Метод: GET
    # Permissions: login_required
    path(
        'employees/<int:pk>/',
        views.EmployeeDetailView.as_view(),
        name='employee_detail'
    ),
    
    # Создать новую запись о сотруднике
    # URL: /employees/create/
    # Метод: GET, POST
    # Permissions: login_required, employees.add_employee
    path(
        'employees/create/',
        views.EmployeeCreateView.as_view(),
        name='employee_create'
    ),
    
    # Редактировать информацию о сотруднике
    # URL: /employees/<id>/edit/
    # Метод: GET, POST
    # Permissions: login_required, employees.change_employee
    path(
        'employees/<int:pk>/edit/',
        views.EmployeeUpdateView.as_view(),
        name='employee_update'
    ),
    
    # Удалить/отключить сотрудника (soft-delete)
    # URL: /employees/<id>/delete/
    # Метод: GET, POST
    # Permissions: login_required, employees.delete_employee
    path(
        'employees/<int:pk>/delete/',
        views.EmployeeDeleteView.as_view(),
        name='employee_delete'
    ),
    
    # ===== ОТДЕЛЕНИЯ (DEPARTMENTS) =====
    # Получить список всех активных отделений
    # URL: /departments/
    # Метод: GET
    # Permissions: login_required
    path(
        'departments/',
        views.DepartmentListView.as_view(),
        name='department_list'
    ),
    
    # Получить информацию об отделении со всеми его сотрудниками
    # URL: /departments/<id>/
    # Метод: GET
    # Permissions: login_required
    path(
        'departments/<int:pk>/',
        views.DepartmentDetailView.as_view(),
        name='department_detail'
    ),
    
    # ===== ДОЛЖНОСТИ (POSITIONS) =====
    # Получить список всех должностей с информацией о количестве сотрудников
    # URL: /positions/
    # Метод: GET
    # Permissions: login_required
    path(
        'positions/',
        views.PositionListView.as_view(),
        name='position_list'
    ),
    
    # ===== СПЕЦИАЛЬНЫЕ ПРЕДСТАВЛЕНИЯ =====
    # Получить список контактных лиц для коммуникаций с родителями
    # Фильтруются по статусу ACTIVE и флагу is_contact_person
    # URL: /contact-persons/
    # Метод: GET (с поддержкой фильтров: search, department)
    # Permissions: login_required
    # Используется: система отправки уведомлений родителям
    path(
        'contact-persons/',
        views.contact_persons_list,
        name='contact_persons_list'
    ),
    
    # Получить расписание работы конкретного сотрудника
    # Показывает рабочие часы и время консультаций с родителями
    # URL: /employees/<id>/schedule/
    # Метод: GET
    # Permissions: login_required
    path(
        'employees/<int:pk>/schedule/',
        views.employee_schedule_view,
        name='employee_schedule'
    ),
    
    # ===== API ЭНДПОИНТЫ (для JavaScript и интеграции) =====
    # API: Получить информацию о сотруднике по ID в формате JSON
    # Используется для асинхронной загрузки данных во фронтенде
    # Параметры: id (табельный номер сотрудника)
    # Возвращает: JSON с полной информацией сотрудника
    # Пример: /api/employee/?id=СОТ-001
    # URL: /api/employee/
    # Метод: GET
    # Permissions: login_required
    # Response: {"id": 1, "employee_id": "СОТ-001", "full_name": "...", ...}
    path(
        'api/employee/',
        views.api_get_employee_by_id,
        name='api_get_employee'
    ),
    
    # ===== ЭКСПОРТ ДАННЫХ =====
    # Экспортировать список активных сотрудников в CSV формат
    # Используется для аналитики, отчётности и интеграции с другими системами
    # Возвращает: CSV файл с полной информацией о сотрудниках
    # Формат: Табельный №; Фамилия; Имя; Должность; Отдел; Email; Телефон; Дата найма
    # URL: /export/employees-csv/
    # Метод: GET
    # Permissions: login_required, employees.view_employee
    path(
        'export/employees-csv/',
        views.export_employees_list,
        name='export_employees_csv'
    ),
]
