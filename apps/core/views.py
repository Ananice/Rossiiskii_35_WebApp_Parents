"""================================================================================
МОДУЛЬ: college_portal.views
ОПИСАНИЕ: Представления (views) для главного приложения колледжа
КОМПЕТЕНЦИИ: ПК-1, ПК-7, ПК-9, ПК-11
================================================================================

ФУНКЦИОНАЛ:
  - Аутентификация пользователя (вход/выход)
  - Дашборды для разных ролей (админ, сотрудник, родитель)
  - API для работы с сообщениями
  - Обработка ошибок

РОЛИ ПОЛЬЗОВАТЕЛЕЙ:
  1. Администратор (administrator) - полный доступ к системе
  2. Сотрудник (staff) - доступ к студентам и сообщениям
  3. Родитель (parent) - доступ только к информации о своём ребёнке
  4. Гость (guest) - нет доступа (перенаправление на login)
"""

# ==============================================================================
# РАЗДЕЛ 1: ИМПОРТЫ
# ==============================================================================

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils.timezone import now
import json

from apps.communications.models import User, Message
from apps.students.models import Student
from apps.employees.models import Employee
from apps.parents.models import Parent


# ==============================================================================
# РАЗДЕЛ 2: ГЛАВНАЯ СТРАНИЦА
# ==============================================================================

def index(request):
    """
    ENDPOINT: GET /
    ОПИСАНИЕ: Главная страница приложения
    
    ЛОГИКА:
      - Если пользователь авторизован → редирект на /dashboard/
      - Если не авторизован → редирект на /login/
    
    ПАРАМЕТРЫ:
      request (HttpRequest): Объект запроса
    
    ВОЗВРАЩАЕТ:
      HttpResponseRedirect: Редирект на dashboard или login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# ==============================================================================
# РАЗДЕЛ 3: АУТЕНТИФИКАЦИЯ
# ==============================================================================

@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    ENDPOINT: GET/POST /login/
    ОПИСАНИЕ: Страница входа в систему
    
    GET: Показать форму входа
    POST: Обработать данные формы входа
    
    ПОЛЯ ФОРМЫ (POST):
      username (str): Логин пользователя (обязательное)
      password (str): Пароль (обязательное)
    
    ПРИМЕРЫ:
      # GET запрос
      curl -X GET http://localhost:8000/login/
      
      # POST запрос
      curl -X POST http://localhost:8000/login/ \\
        -d "username=ivanov&password=secret123"
    
    ВОЗВРАЩАЕТ (GET):
      HttpResponse: Рендер шаблона auth/login.html
    
    ВОЗВРАЩАЕТ (POST - успех):
      HttpResponseRedirect: Редирект на /dashboard/
    
    ВОЗВРАЩАЕТ (POST - ошибка):
      HttpResponse: Рендер login.html с сообщением об ошибке
    """
    
    # ⭐ ОБРАБОТКА GET ЗАПРОСА
    if request.method == 'GET':
        # Если уже авторизован, перенаправляем на дашборд
        if request.user.is_authenticated:
            return redirect('dashboard')
        # Показываем форму входа
        return render(request, 'auth/login.html')
    
    # ⭐ ОБРАБОТКА POST ЗАПРОСА
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Проверяем, что оба поля заполнены
        if not username or not password:
            return render(request, 'auth/login.html', {
                'error': 'Заполните оба поля (логин и пароль)'
            })
        
        # Проверяем учётные данные через Django auth
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Успешная аутентификация - создаём сессию
            login(request, user)
            return redirect('dashboard')
        else:
            # Неверный логин или пароль
            return render(request, 'auth/login.html', {
                'error': 'Неверный логин или пароль. Попробуйте снова.',
                'username': username  # Возвращаем введённый логин
            })


@login_required(login_url='login')
def logout_view(request):
    """
    ENDPOINT: GET /logout/
    ОПИСАНИЕ: Выход из системы
    
    ТРЕБУЕТ:
      - Пользователь должен быть авторизован (@login_required)
    
    ЛОГИКА:
      1. Разрушаем сессию пользователя
      2. Перенаправляем на страницу входа
    
    ВОЗВРАЩАЕТ:
      HttpResponseRedirect: Редирект на /login/
    """
    logout(request)
    return redirect('login')


# ==============================================================================
# РАЗДЕЛ 4: ДАШБОРДЫ ДЛЯ РАЗНЫХ РОЛЕЙ
# ==============================================================================

@login_required(login_url='login')
def dashboard(request):
    """
    ENDPOINT: GET /dashboard/
    ОПИСАНИЕ: Главный дашборд пользователя (версия зависит от роли)
    
    ТРЕБУЕТ:
      - Пользователь должен быть авторизован
    
    РОЛЕВАЯ ЛОГИКА:
      1. АДМИНИСТРАТОР (administrator):
         - Видит статистику по всем пользователям
         - Видит список всех пользователей системы
         - Видит количество сообщений и активных сессий
      
      2. СОТРУДНИК (staff):
         - Видит список назначенных студентов
         - Видит непрочитанные сообщения
         - Видит отчёты за текущий день
         - Видит последние сообщения в чате
      
      3. РОДИТЕЛЬ (parent):
         - Видит информацию о своём ребёнке
         - Видит оценки (GPA), группу, специальность
         - Видит непрочитанные сообщения от сотрудников
         - Видит последние сообщения в чате
      
      4. ГОСТЬ (guest):
         - Видит базовый дашборд родителя
    
    ПАРАМЕТРЫ:
      request (HttpRequest): Объект запроса
    
    ПРИМЕРЫ КОНТЕКСТА (для админа):
      {
        'user': <User: admin>,
        'role': 'administrator',
        'users_count': 150,
        'messages_count': 2340,
        'active_sessions': 42,
        'users': [<User: student1>, <User: staff1>, ...]
      }
    
    ВОЗВРАЩАЕТ:
      HttpResponse: Рендер соответствующего шаблона дашборда
    """
    
    user = request.user
    role = getattr(user, 'role', 'guest')
    
    # Базовый контекст для всех ролей
    context = {'user': user, 'role': role}
    
    # ⭐ ДАШБОРД АДМИНИСТРАТОРА
    if role == 'administrator':
        context.update({
            'users_count': User.objects.count(),
            'messages_count': Message.objects.count(),
            'active_sessions': User.objects.filter(last_login__isnull=False).count(),
            'users': User.objects.all()[:50],  # Первые 50 пользователей
        })
        return render(request, 'dashboard/admin.html', context)
    
    # ⭐ ДАШБОРД СОТРУДНИКА
    elif role == 'staff':
        try:
            employee = Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            employee = None
        
        context.update({
            'employee': employee,
            'unread_messages': Message.objects.filter(recipient=user, is_read=False).count(),
            'assigned_students': Student.objects.filter(advisor=employee).count() if employee else 0,
            'pending_reports': Message.objects.filter(sender=user, created_at__date=now().date()).count(),
            'recent_messages': Message.objects.filter(
                Q(sender=user) | Q(recipient=user)
            ).order_by('-created_at')[:5],
        })
        return render(request, 'dashboard/staff.html', context)
    
    # ⭐ ДАШБОРД РОДИТЕЛЯ
    elif role == 'parent':
        try:
            parent = Parent.objects.get(user=user)
        except Parent.DoesNotExist:
            parent = None
        
        student = None
        if parent:
            try:
                student = Student.objects.get(parent=parent)
            except Student.DoesNotExist:
                student = None
        
        context.update({
            'parent': parent,
            'student_name': student.full_name if student else 'Не привязан',
            'student_group': student.group if student else '-',
            'student_specialty': student.specialty if student else '-',
            'student_id': student.student_id if student else '-',
            'gpa': student.gpa if student else '-',
            'unread_messages': Message.objects.filter(recipient=user, is_read=False).count(),
            'recent_messages': Message.objects.filter(recipient=user).order_by('-created_at')[:5],
        })
        return render(request, 'dashboard/parent.html', context)
    
    # ⭐ ДАШБОРД ДЛЯ ГОСТЕЙ
    return render(request, 'dashboard/parent.html', context)


# ==============================================================================
# РАЗДЕЛ 5: МОДУЛЬ СООБЩЕНИЙ
# ==============================================================================

@login_required(login_url='login')
def messages_view(request):
    """
    ENDPOINT: GET /messages/
    ОПИСАНИЕ: Страница сообщений (список контактов)
    
    ТРЕБУЕТ:
      - Пользователь должен быть авторизован
    
    ЛОГИКА:
      1. Получаем все контакты пользователя (с кем он переписывался)
      2. Для каждого контакта считаем непрочитанные сообщения
      3. Возвращаем список контактов с информацией о сообщениях
    
    ПАРАМЕТРЫ:
      request (HttpRequest): Объект запроса
    
    ВОЗВРАЩАЕТ:
      HttpResponse: Рендер шаблона messages/messages.html с контактами
    """
    
    user = request.user
    contact_ids = set()
    
    # Получаем ID всех, кто отправлял сообщения этому пользователю
    sent_to_me = Message.objects.filter(recipient=user).values_list('sender_id', flat=True)
    contact_ids.update(sent_to_me)
    
    # Получаем ID всех, кому этот пользователь отправлял сообщения
    sent_by_me = Message.objects.filter(sender=user).values_list('recipient_id', flat=True)
    contact_ids.update(sent_by_me)
    
    # Получаем объекты User для этих контактов
    contacts = User.objects.filter(id__in=contact_ids)
    
    # Подготавливаем данные контактов
    contacts_data = []
    for contact in contacts:
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
    
    context = {
        'user': user,
        'contacts': contacts_data
    }
    return render(request, 'messages/messages.html', context)


@login_required(login_url='login')
def api_messages(request):
    """
    ENDPOINT: GET /api/messages/
    ОПИСАНИЕ: API для получения сообщений с конкретным контактом
    
    ТРЕБУЕТ:
      - Пользователь должен быть авторизован
    
    ПАРАМЕТРЫ QUERY:
      contact_id (int): ID контакта (обязательное)
    
    ПРИМЕРЫ:
      curl "http://localhost:8000/api/messages/?contact_id=5"
    
    ЛОГИКА:
      1. Получаем ID контакта из параметров
      2. Получаем все сообщения между пользователем и контактом
      3. Отмечаем полученные сообщения как прочитанные
      4. Возвращаем JSON со списком сообщений
    
    ВОЗВРАЩАЕТ:
      JSON: {
        "messages": [
          {
            "id": 1,
            "sender_id": 2,
            "sender_name": "Иван Петров",
            "content": "Привет!",
            "created_at": "2025-12-28 15:30:45",
            "is_read": true
          },
          ...
        ]
      }
    """
    
    contact_id = request.GET.get('contact_id')
    if not contact_id:
        return JsonResponse({'error': 'contact_id обязателен'}, status=400)
    
    user = request.user
    try:
        contact = User.objects.get(id=contact_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Контакт не найден'}, status=404)
    
    # Получаем все сообщения между пользователями
    messages = Message.objects.filter(
        Q(sender=user, recipient=contact) | Q(sender=contact, recipient=user)
    ).order_by('created_at')
    
    # Отмечаем сообщения от контакта как прочитанные
    Message.objects.filter(
        sender=contact,
        recipient=user,
        is_read=False
    ).update(is_read=True)
    
    # Форматируем сообщения для JSON
    messages_data = [{
        'id': msg.id,
        'sender_id': msg.sender.id,
        'sender_name': msg.sender.get_full_name() or msg.sender.username,
        'content': msg.content,
        'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': msg.is_read,
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})


@login_required(login_url='login')
@require_http_methods(["POST"])
def api_send_message(request):
    """
    ENDPOINT: POST /api/messages/send/
    ОПИСАНИЕ: API для отправки сообщения
    
    ТРЕБУЕТ:
      - Пользователь должен быть авторизован
      - Метод запроса: POST
    
    ТЕЛО ЗАПРОСА (JSON):
      {
        "recipient_id": 5,
        "content": "Привет, как дела?"
      }
    
    ПРИМЕРЫ:
      curl -X POST http://localhost:8000/api/messages/send/ \\
        -H "Content-Type: application/json" \\
        -d '{"recipient_id": 5, "content": "Привет!"}'
    
    ЛОГИКА:
      1. Парсим JSON из тела запроса
      2. Проверяем наличие обязательных полей
      3. Находим получателя в БД
      4. Создаём новое сообщение
      5. Возвращаем JSON с информацией о созданном сообщении
    
    ВОЗВРАЩАЕТ (успех):
      JSON 200: {
        "success": true,
        "message": {
          "id": 42,
          "sender_id": 1,
          "sender_name": "Петров Иван",
          "content": "Привет!",
          "created_at": "2025-12-28 15:35:20"
        }
      }
    
    ВОЗВРАЩАЕТ (ошибка):
      JSON 400: {"error": "recipient_id и content обязательны"}
      JSON 404: {"error": "Получатель не найден"}
      JSON 400: {"error": "Неверный JSON"}
    """
    
    try:
        # Парсим JSON из тела запроса
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        content = data.get('content', '').strip()
        
        # Проверяем, что оба поля заполнены
        if not recipient_id or not content:
            return JsonResponse(
                {'error': 'recipient_id и content обязательны'},
                status=400
            )
        
        # Получаем получателя из БД
        recipient = User.objects.get(id=recipient_id)
        
        # Создаём новое сообщение
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        
        # Возвращаем информацию о созданном сообщении
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender_id': message.sender.id,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'content': message.content,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'Получатель не найден'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==============================================================================
# РАЗДЕЛ 6: ОБРАБОТЧИКИ ОШИБОК
# ==============================================================================

def page_not_found(request, exception):
    """
    ОБРАБОТЧИК: 404 Not Found
    ОПИСАНИЕ: Страница ошибки 404 (страница не найдена)
    
    КОГДА ВЫЗЫВАЕТСЯ:
      - Пользователь обращается к несуществующему URL
    
    ВОЗВРАЩАЕТ:
      HttpResponse: Рендер шаблона errors/404.html со статусом 404
    """
    return render(request, 'errors/404.html', status=404)


def server_error(request):
    """
    ОБРАБОТЧИК: 500 Internal Server Error
    ОПИСАНИЕ: Страница ошибки 500 (ошибка сервера)
    
    КОГДА ВЫЗЫВАЕТСЯ:
      - На сервере произошла необработанная ошибка
    
    ВОЗВРАЩАЕТ:
      HttpResponse: Рендер шаблона errors/500.html со статусом 500
    """
    return render(request, 'errors/500.html', status=500)
