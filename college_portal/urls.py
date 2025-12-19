# ===================== ИМПОРТЫ =====================
from django.urls import path
from . import views  # Импортируем функции из views.py

# ===================== МАРШРУТЫ (URLS) =====================
# Определяем, какой URL соответствует какой функции

urlpatterns = [
    # Главная страница (/)
    # Если пользователь зашёл на главную, перенаправит его на логин или dashboard
    path('', views.index, name='index'),
    
    # Страница входа (/login/)
    # GET: показать форму
    # POST: обработать отправку формы
    path('login/', views.login_view, name='login'),
    
    # Выход (/logout/)
    # Разлогинить пользователя и вернуть на логин
    path('logout/', views.logout_view, name='logout'),
    
    # Панель управления (/dashboard/)
    # Главная страница после входа
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Сообщения (/messages/)
    # Интерфейс сообщений
    path('messages/', views.messages_view, name='messages'),
    
    # ===================== API ENDPOINTS =====================
    # Это AJAX запросы без перезагрузки страницы
    
    # API: получить сообщения (/api/messages/)
    # GET параметр: contact_id
    path('api/messages/', views.api_messages, name='api_messages'),
    
    # API: отправить сообщение (/api/messages/send/)
    # POST параметры: recipient_id, content
    path('api/messages/send/', views.api_send_message, name='api_send_message'),
]

# ===================== ОБРАБОТКА ОШИБОК =====================
# Что показать, если возникла ошибка

handler404 = 'college_portal.views.page_not_found'  # Ошибка 404
handler500 = 'college_portal.views.server_error'    # Ошибка 500
