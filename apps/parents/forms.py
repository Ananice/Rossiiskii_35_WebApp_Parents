"""
Формы для создания и редактирования данных о родителях.

Включает:
- ParentForm - форма для создания/редактирования родителей
- ParentStudentRelationForm - форма для связей родитель-студент
- RelationTypeForm - форма для типов связей
- ParentBulkImportForm - форма для массового импорта (бонус)

Компетенция ПК-1: Создание и управление информационными ресурсами.
Компетенция ПК-7: Разработка бизнес-приложений.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Parent, ParentStudentRelation, RelationType


class RelationTypeForm(forms.ModelForm):
    """Форма для создания и редактирования типов родственных связей."""
    
    class Meta:
        model = RelationType
        fields = ('name', 'code', 'description', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Мать, Отец, Опекун'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: MOTHER, FATHER, GUARDIAN',
                'style': 'text-transform: uppercase;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание типа связи'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_code(self):
        """Преобразует код в заглавные буквы и проверяет уникальность."""
        code = self.cleaned_data.get('code', '').upper()
        
        # Проверяем на уникальность
        if self.instance.pk:
            # При редактировании
            if RelationType.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Код уже существует в системе.')
        else:
            # При создании
            if RelationType.objects.filter(code=code).exists():
                raise ValidationError('Код уже существует в системе.')
        
        return code


class ParentForm(forms.ModelForm):
    """Форма для создания и редактирования данных о родителях/опекунах."""
    
    class Meta:
        model = Parent
        fields = (
            'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender',
            'email', 'phone', 'phone_secondary',
            'messenger', 'messenger_id',
            'country', 'city', 'street_address', 'postal_code',
            'employer', 'job_position', 'work_phone',
            'status', 'can_receive_notifications',
            'preferred_contact_method', 'consent_gdpr'
        )
        widgets = {
            # Личная информация
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя',
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия',
                'required': 'required'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Отчество (опционально)'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            
            # Контактная информация
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 123-45-67',
                'required': 'required'
            }),
            'phone_secondary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 765-43-21'
            }),
            'messenger': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telegram, WhatsApp, Viber'
            }),
            'messenger_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@username или +79001234567'
            }),
            
            # Адрес
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Россия'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Москва'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ул. Примерная, д. 1, кв. 1'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456'
            }),
            
            # Работа
            'employer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название организации'
            }),
            'job_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Должность'
            }),
            'work_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 123-45-67'
            }),
            
            # Статус и права
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'can_receive_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'consent_gdpr': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_email(self):
        """Проверяет уникальность email."""
        email = self.cleaned_data.get('email', '')
        
        if self.instance.pk:
            # При редактировании
            if Parent.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Этот email уже используется в системе.')
        else:
            # При создании
            if Parent.objects.filter(email=email).exists():
                raise ValidationError('Этот email уже используется в системе.')
        
        return email
    
    def clean_phone(self):
        """Проверяет формат и уникальность основного телефона."""
        phone = self.cleaned_data.get('phone', '')
        
        if phone and not phone.replace('+', '').replace(' ', '').replace('(', '').replace(')', '').replace('-', '').isdigit():
            raise ValidationError('Телефон содержит недопустимые символы.')
        
        return phone
    
    def clean(self):
        """Общая проверка формы."""
        cleaned_data = super().clean()
        
        # Если выбран мессенджер, должен быть ID
        messenger = cleaned_data.get('messenger')
        messenger_id = cleaned_data.get('messenger_id')
        
        if messenger and not messenger_id:
            raise ValidationError('Если указан мессенджер, то должен быть указан ID или ник.')
        
        return cleaned_data


class ParentStudentRelationForm(forms.ModelForm):
    """Форма для создания и редактирования связей между родителями и студентами."""
    
    student_id = forms.IntegerField(
        label='ID студента',
        help_text='Укажите ID студента из системы',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Например: 12345'
        })
    )
    
    class Meta:
        model = ParentStudentRelation
        fields = (
            'parent',
            'student_id',
            'relation_type',
            'is_primary_contact',
            'is_active',
            'end_date'
        )
        widgets = {
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'relation_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_primary_contact': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': 'checked'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'parent': 'Родитель/Опекун',
            'relation_type': 'Тип связи',
            'is_primary_contact': 'Основной контакт',
            'is_active': 'Активна',
            'end_date': 'Дата окончания (опционально)',
        }
    
    def clean(self):
        """Проверяет валидность связи."""
        cleaned_data = super().clean()
        
        parent = cleaned_data.get('parent')
        student_id = cleaned_data.get('student_id')
        relation_type = cleaned_data.get('relation_type')
        
        if parent and student_id and relation_type:
            # Проверяем уникальность связи
            existing = ParentStudentRelation.objects.filter(
                parent=parent,
                student_id=student_id,
                relation_type=relation_type
            )
            
            # При редактировании исключаем текущий объект
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    'Такая связь уже существует. '
                    'Один родитель не может иметь две одинаковые связи с одным студентом.'
                )
        
        return cleaned_data


class ParentBulkImportForm(forms.Form):
    """Форма для массового импорта данных о родителях (для будущих версий)."""
    
    csv_file = forms.FileField(
        label='CSV файл',
        help_text='Загружите файл в формате CSV',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )
    
    def clean_csv_file(self):
        """Проверяет расширение файла."""
        file = self.cleaned_data.get('csv_file')
        
        if file:
            if not file.name.endswith('.csv'):
                raise ValidationError('Допустимо загружать только CSV файлы.')
            
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('Размер файла не должен превышать 5MB.')
        
        return file
