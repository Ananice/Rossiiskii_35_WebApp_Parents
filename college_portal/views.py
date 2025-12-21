# ===================== ИМПОРТЫ =====================
# Подключаем библиотеки, которые нам нужны

from django.shortcuts import render, redirect  # render = показать HTML, redirect = перенаправить
from django.contrib.auth import authenticate, login, logout  # Для входа/выхода
from django.contrib.auth.decorators import login_required  # Проверка авторизации
from django.contrib.auth.models import User  # Модель пользователя Django
from django.http import JsonResponse  # Ответ JSON (для AJAX)
from django.views.decorators.http import require_http_methods  # Проверка метода HTTP
from django.db.models import Q  # Для сложных фильтров в БД
from django.utils.timezone import now  # Текущее время
import json  # Работа с JSON

# Подключаем свои модели
from communications.models import Message  # Модель сообщений
from students.models import Student  # Модель студентов
from employees.models import Employee  # Модель сотрудников
from parents.models import Parent  # Модель родителей

# ===================== 1. ФУНКЦИЯ: ГЛАВНАЯ СТРАНИЦА / РЕДИРЕКТ =====================
# Если пользователь зашёл на главную, перенаправить его на логин или панель

def index(request):
    """
    Главная страница приложения
    
    request = объект запроса от браузера
    Возвращает: редирект на /login или /dashboard (в зависимости от авторизации)
    """
    
    # Если пользователь уже авторизован
    if request.user.is_authenticated:
        # Перенаправить его на панель управления
        return redirect('dashboard')
    else:
        # Если нет - перенаправить на страницу входа
        return redirect('login')


# ===================== 2. ФУНКЦИЯ: ЛОГИН (ВХОД В СИСТЕМУ) =====================
# Обработка входа пользователя в систему

@require_http_methods(["GET", "POST"])  # Принимаем GET и POST запросы
def login_view(request):
    """
    Страница входа в систему
    
    GET: показать форму входа
    POST: проверить логин/пароль и войти
    """
    
    # ОБРАБОТКА GET ЗАПРОСА (показ формы)
    if request.method == 'GET':
        # Если пользователь уже авторизован, не показывать логин
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        # Иначе показать форму входа
        return render(request, 'auth/login.html')
    
    # ОБРАБОТКА POST ЗАПРОСА (отправка формы)
    if request.method == 'POST':
        # Получить логин и пароль из формы
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Проверить, заполнены ли оба поля
        if not username or not password:
            # Если нет - показать ошибку
            return render(request, 'auth/login.html', {
                'error': 'Заполните оба поля'
            })
        
        # Проверить учётные данные
        # authenticate = найти пользователя с таким логином и паролем
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Если пользователь найден и пароль правильный
            
            # Войти в систему
            login(request, user)
            
            # Перенаправить на панель управления
            return redirect('dashboard')
        else:
            # Если логин/пароль неправильные
            return render(request, 'auth/login.html', {
                'error': '❌ Неверный логин или пароль'
            })


# ===================== 3. ФУНКЦИЯ: ВЫХОД ИЗ СИСТЕМЫ =====================
# Разлогинить пользователя и перенаправить на логин

@login_required(login_url='login')  # Проверка: пользователь должен быть авторизован
def logout_view(request):
    """
    Выход из системы
    """
    
    # Разлогинить пользователя
    logout(request)
    
    # Перенаправить на страницу входа
    return redirect('login')


# ===================== 4. ФУНКЦИЯ: ПАНЕЛЬ УПРАВЛЕНИЯ (DASHBOARD) =====================
# Главная страница после входа (разная для каждой роли)

@login_required(login_url='login')  # Только для авторизованных
def dashboard(request):
    """
    Панель управления (dashboard)
    Зависит от роли пользователя:
    - Администратор → admin.html
    - Сотрудник → staff.html
    - Родитель → parent.html
    """
    
    user = request.user  # Текущий пользователь
    
    # Получить роль пользователя (из поля в профиле User)
    # Примечание: поле role должно быть в модели User
    role = getattr(user, 'role', 'guest')  # Если роли нет, роль = guest
    
    # CONTEXT = словарь с данными для HTML шаблона
    context = {
        'user': user,  # Пользователь
        'role': role,  # Его роль
    }
    
    # ЛОГИКА ДЛЯ АДМИНИСТРАТОРА
    if role == 'administrator':
        # Получить статистику для админ-панели
        context.update({
            'users_count': User.objects.count(),  # Всего пользователей
            'messages_count': Message.objects.count(),  # Всего сообщений
            'active_sessions': User.objects.filter(
                last_login__isnull=False  # Те, кто хотя бы раз заходил
            ).count(),
            'users': User.objects.all()[:50],  # Первые 50 пользователей
        })
        
        # Показать админ-панель
        return render(request, 'dashboard/admin.html', context)
    
    # ЛОГИКА ДЛЯ СОТРУДНИКА
    elif role == 'staff':
        # Получить данные сотрудника
        try:
            employee = Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            employee = None
        
        # Получить статистику
        context.update({
            'employee': employee,
            'unread_messages': Message.objects.filter(
                recipient=user,
                is_read=False  # Непрочитанные сообщения
            ).count(),
            'assigned_students': Student.objects.filter(
                advisor=employee  # Студенты под присмотром этого сотрудника
            ).count() if employee else 0,
            'pending_reports': Message.objects.filter(
                sender=user,
                created_at__gte=now()  # За последний день
            ).count(),
            'recent_messages': Message.objects.filter(
                Q(sender=user) | Q(recipient=user)  # От пользователя или к нему
            ).order_by('-created_at')[:5],  # Последние 5
        })
        
        # Показать панель сотрудника
        return render(request, 'dashboard/staff.html', context)
    
    # ЛОГИКА ДЛЯ РОДИТЕЛЯ
    elif role == 'parent':
        # Получить родителя
        try:
            parent = Parent.objects.get(user=user)
        except Parent.DoesNotExist:
            parent = None
        
        # Получить студента (ребёнка)
        student = None
        if parent:
            try:
                student = Student.objects.get(parent=parent)
            except Student.DoesNotExist:
                student = None
        
        # Получить статистику
        context.update({
            'parent': parent,
            'student_name': student.full_name if student else 'Не привязан',
            'student_group': student.group if student else '-',
            'student_specialty': student.specialty if student else '-',
            'student_id': student.student_id if student else '-',
            'gpa': student.gpa if student else '-',
            'unread_messages': Message.objects.filter(
                recipient=user,
                is_read=False
            ).count(),
            'recent_messages': Message.objects.filter(
                recipient=user
            ).order_by('-created_at')[:5],
        })
        
        # Показать панель родителя
        return render(request, 'dashboard/parent.html', context)
    
    # ЕСЛИ РОЛЬ НЕ ОПРЕДЕЛЕНА
    else:
        # Показать стандартную панель
        return render(request, 'dashboard/parent.html', context)


# ===================== 5. ФУНКЦИЯ: СПИСОК СООБЩЕНИЙ =====================
# Отображение интерфейса сообщений

@login_required(login_url='login')
def messages_view(request):
    """
    Страница сообщений
    
    Показывает:
    - Список контактов (левая сторона)
    - Чат с выбранным контактом (правая сторона)
    """
    
    user = request.user
    
    # Получить всех контактов (те, кто переписывался с пользователем)
    # Объединяем тех, кто послал сообщение, и тех, кому пользователь писал
    contact_ids = set()
    
    # От кого пришли сообщения
    sent_messages = Message.objects.filter(recipient=user).values_list('sender_id', flat=True)
    contact_ids.update(sent_messages)
    
    # Кому пишет пользователь
    received_messages = Message.objects.filter(sender=user).values_list('recipient_id', flat=True)
    contact_ids.update(received_messages)
    
    # Получить объекты контактов
    contacts = User.objects.filter(id__in=contact_ids)
    
    # Подготовить данные о контактах
    contacts_data = []
    for contact in contacts:
        # Подсчитать непрочитанные сообщения от этого контакта
        unread_count = Message.objects.filter(
            sender=contact,
            recipient=user,
            is_read=False
        ).count()
        
        contacts_data.append({
            'id': contact.id,
            'name': contact.get_full_name() or contact.username,
            'unread_count': unread_count,
        })
    
    # Подготовить контекст
    context = {
        'user': user,
        'contacts': contacts_data,
    }
    
    # Показать страницу сообщений
    return render(request, 'messages/messages.html', context)


# ===================== 6. API: ПОЛУЧИТЬ СООБЩЕНИЯ С КОНТАКТОМ =====================
# AJAX запрос: загрузить сообщения с конкретным пользователем

@login_required(login_url='login')
@require_http_methods(["GET"])
def api_messages(request):
    """
    API endpoint для загрузки сообщений
    
    Параметры:
    - contact_id = ID контакта, с которым загружаем переписку
    
    Возвращает: JSON с сообщениями
    """
    
    user = request.user
    contact_id = request.GET.get('contact_id')
    
    # Проверить параметр
    if not contact_id:
        return JsonResponse({'error': 'contact_id не указан'}, status=400)
    
    try:
        # Получить контакт
        contact = User.objects.get(id=contact_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Контакт не найден'}, status=404)
    
    # Получить все сообщения между пользователем и контактом
    messages = Message.objects.filter(
        Q(sender=user, recipient=contact) |  # От пользователя к контакту
        Q(sender=contact, recipient=user)     # От контакта к пользователю
    ).order_by('created_at')
    
    # Отметить как прочитанные
    Message.objects.filter(sender=contact, recipient=user, is_read=False).update(is_read=True)
    
    # Подготовить данные
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.get_full_name() or msg.sender.username,
            'content': msg.content,
            'time': msg.created_at.strftime('%d.%m.%Y %H:%M'),  # Формат даты
            'is_outgoing': msg.sender == user,  # Это исходящее или входящее
        })
    
    # Ответить JSON
    return JsonResponse({
        'contact_name': contact.get_full_name() or contact.username,
        'contact_role': getattr(contact, 'role', 'unknown'),
        'messages': messages_data,
    })


# ===================== 7. API: ОТПРАВИТЬ СООБЩЕНИЕ =====================
# AJAX запрос: отправить новое сообщение

@login_required(login_url='login')
@require_http_methods(["POST"])
def api_send_message(request):
    """
    API endpoint для отправки сообщения
    
    Параметры:
    - recipient_id = кому отправляем
    - content = текст сообщения
    
    Возвращает: JSON с результатом
    """
    
    user = request.user
    recipient_id = request.POST.get('recipient_id')
    content = request.POST.get('content', '').strip()
    
    # Проверить параметры
    if not recipient_id or not content:
        return JsonResponse({'success': False, 'message': 'Заполните все поля'})
    
    try:
        # Получить получателя
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Получатель не найден'})
    
    try:
        # Создать новое сообщение
        message = Message.objects.create(
            sender=user,
            recipient=recipient,
            content=content
        )
        
        # Вернуть успех
        return JsonResponse({
            'success': True,
            'message': 'Сообщение отправлено',
            'message_id': message.id
        })
    
    except Exception as e:
        # Если ошибка
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


# ===================== 8. ФУНКЦИЯ: 404 (СТРАНИЦА НЕ НАЙДЕНА) =====================
# Показать ошибку если пользователь зашёл на несуществующую страницу

def page_not_found(request, exception):
    """
    Обработка ошибки 404
    """
    return render(request, '404.html', status=404)


# ===================== 9. ФУНКЦИЯ: 500 (ОШИБКА СЕРВЕРА) =====================
# Показать ошибку если что-то сломалось на сервере

def server_error(request):
    """
    Обработка ошибки 500
    """
    return render(request, '500.html', status=500)
