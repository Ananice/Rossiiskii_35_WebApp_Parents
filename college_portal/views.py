# =====================================================================================
# ФАЙЛ: college_portal/views.py
# ОПИСАНИЕ: Главные views для аутентификации, дашбордов и сообщений
# КОМПЕТЕНЦИИ: ПК-1, ПК-7, ПК-9, ПК-11
# =====================================================================================

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils.timezone import now
import json

from communications.models import User, Message
from students.models import Student
from employees.models import Employee
from parents.models import Parent


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'auth/login.html')
    
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    
    if not username or not password:
        return render(request, 'auth/login.html', {'error': 'Заполните оба поля'})
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'auth/login.html', {'error': 'Неверный логин или пароль'})


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    user = request.user
    role = getattr(user, 'role', 'guest')
    
    context = {'user': user, 'role': role}
    
    if role == 'administrator':
        context.update({
            'users_count': User.objects.count(),
            'messages_count': Message.objects.count(),
            'active_sessions': User.objects.filter(last_login__isnull=False).count(),
            'users': User.objects.all()[:50],
        })
        return render(request, 'dashboard/admin.html', context)
    
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
            'recent_messages': Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-created_at')[:5],
        })
        return render(request, 'dashboard/staff.html', context)
    
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
    
    return render(request, 'dashboard/parent.html', context)


@login_required(login_url='login')
def messages_view(request):
    user = request.user
    contact_ids = set()
    
    sent_messages = Message.objects.filter(recipient=user).values_list('sender_id', flat=True)
    contact_ids.update(sent_messages)
    
    received_messages = Message.objects.filter(sender=user).values_list('recipient_id', flat=True)
    contact_ids.update(received_messages)
    
    contacts = User.objects.filter(id__in=contact_ids)
    
    contacts_data = []
    for contact in contacts:
        unread_count = Message.objects.filter(sender=contact, recipient=user, is_read=False).count()
        contacts_data.append({
            'id': contact.id,
            'name': contact.get_full_name() or contact.username,
            'unread_count': unread_count,
        })
    
    context = {'user': user, 'contacts': contacts_data}
    return render(request, 'messages/messages.html', context)


@login_required(login_url='login')
def api_messages(request):
    contact_id = request.GET.get('contact_id')
    if not contact_id:
        return JsonResponse({'error': 'contact_id обязателен'}, status=400)
    
    user = request.user
    try:
        contact = User.objects.get(id=contact_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Контакт не найден'}, status=404)
    
    messages = Message.objects.filter(
        Q(sender=user, recipient=contact) | Q(sender=contact, recipient=user)
    ).order_by('created_at')
    
    Message.objects.filter(sender=contact, recipient=user, is_read=False).update(is_read=True)
    
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
    try:
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        content = data.get('content', '').strip()
        
        if not recipient_id or not content:
            return JsonResponse({'error': 'recipient_id и content обязательны'}, status=400)
        
        recipient = User.objects.get(id=recipient_id)
        
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        
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


def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)


def server_error(request):
    return render(request, 'errors/500.html', status=500)