"""
Formы Django для ввода и фильтрации данных о сотрудниках.
Обеспечивает валидацию, удобство использования и защиту от ошибок.

Компетенция ПК-1.2: Уметь проводить анализ потребностей пользователей информационных ресурсов предприятия.
"""

from django import forms
from django.forms import ModelForm, ModelMultipleChoiceField, DateInput, TextInput
from .models import Employee, Department, Position, Qualification, EmployeeSchedule


class EmployeeForm(ModelForm):
    """
    Форма для создания и редактирования данных о сотрудниках.
    Включает валидацию email, телефонных номеров и проверку статуса.
    """
    qualifications = ModelMultipleChoiceField(
        queryset=Qualification.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Квалификации и сертификаты'
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender',
            'email', 'phone', 'mobile_phone',
            'employee_id', 'position', 'department',
            'qualifications', 'office_room',
            'status', 'termination_date',
            'photo', 'biography',
            'is_contact_person', 'can_send_notifications'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию',
                'required': True
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество (опционально)'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@university.ru',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67',
                'required': True
            }),
            'mobile_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'СОТ-001',
                'required': True
            }),
            'position': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'office_room': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '305'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'termination_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Биография и достижения сотрудника'
            }),
            'is_contact_person': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'can_send_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        """
        Дополнительная валидация формы.
        Проверяет консистентность дат и статусов.
        """
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        termination_date = cleaned_data.get('termination_date')

        # Если сотрудник уволен, дата увольнения должна быть указана
        if status == 'DISMISSED' and not termination_date:
            self.add_error('termination_date',
                          'Дата увольнения обязательна для уволенных сотрудников')

        # Если статус не увольнение, дата увольнения должна быть пуста
        if status != 'DISMISSED' and termination_date:
            self.add_error('status',
                          'Дата увольнения может быть указана только для уволенных')

        return cleaned_data


class EmployeeFilterForm(forms.Form):
    """
    Форма фильтрации и поиска сотрудников.
    Позволяет быстро найти нужного сотрудника по различным критериям.
    """
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ФИО, Email, табельный номер...'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        label='Отдел',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    position = forms.ModelChoiceField(
        queryset=Position.objects.filter(is_active=True),
        required=False,
        label='Должность',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[('', '---')] + Employee.STATUS_CHOICES,
        required=False,
        label='Статус',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    is_contact = forms.ChoiceField(
        choices=[('', '---'), ('true', 'Контактные лица'), ('false', 'Остальные')],
        required=False,
        label='Тип',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class DepartmentForm(ModelForm):
    """
    Форма для создания и редактирования отделов.
    Поддерживает иерархию отделов и назначение руководителей.
    """

    class Meta:
        model = Department
        fields = [
            'name', 'code', 'description',
            'parent_department', 'head_of_department',
            'email', 'phone', 'office_location', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название отдела',
                'required': True
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ОТД-001',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание функций и ответственности'
            }),
            'parent_department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'head_of_department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'department@university.ru'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (495) 000-00-00'
            }),
            'office_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2 этаж, каб. 205'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class PositionForm(ModelForm):
    """
    Форма для создания и редактирования должностей.
    Включает требования к квалификации, опыту и диапазон зарплаты.
    """

    class Meta:
        model = Position
        fields = [
            'name', 'code', 'level', 'department_category',
            'description', 'required_education', 'required_experience_years',
            'salary_range_min', 'salary_range_max', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название должности',
                'required': True
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ДОЛЯ-001',
                'required': True
            }),
            'level': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'department_category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Педагогический',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Описание обязанностей и требований'
            }),
            'required_education': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Высшее образование'
            }),
            'required_experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '5'
            }),
            'salary_range_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': '50000'
            }),
            'salary_range_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': '100000'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class QualificationForm(ModelForm):
    """
    Форма для создания и редактирования квалификаций и сертификатов.
    """

    class Meta:
        model = Qualification
        fields = [
            'name', 'code', 'type', 'issuing_organization',
            'description', 'is_mandatory', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название квалификации',
                'required': True
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'КВАЛ-001',
                'required': True
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'issuing_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Организация-издатель'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_mandatory': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class EmployeeScheduleForm(ModelForm):
    """
    Форма для редактирования рабочего графика и времени консультаций.
    Позволяет указать часы работы для каждого дня недели и время консультаций.
    """

    class Meta:
        model = EmployeeSchedule
        fields = [
            'monday_start', 'monday_end',
            'tuesday_start', 'tuesday_end',
            'wednesday_start', 'wednesday_end',
            'thursday_start', 'thursday_end',
            'friday_start', 'friday_end',
            'saturday_start', 'saturday_end',
            'sunday_start', 'sunday_end',
            'consultation_hours'
        ]
        widgets = {
            'monday_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'monday_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'tuesday_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'tuesday_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'wednesday_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'wednesday_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'thursday_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'thursday_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'friday_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'friday_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'saturday_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'saturday_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'sunday_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'sunday_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'consultation_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'пн-чт 16:00-18:00, сб 10:00-12:00'
            }),
        }
