/* ===================== КОГДА СТРАНИЦА ЗАГРУЖЕНА ===================== */
// Этот код выполнится ДО того, как пользователь начнёт взаимодействовать

document.addEventListener('DOMContentLoaded', function() {
    // DOMContentLoaded = когда вся HTML загружена
    
    console.log('✅ Приложение загружено');
    // console.log = вывести сообщение в консоль браузера (F12)
    
    // ========== ИНИЦИАЛИЗАЦИЯ КОМПОНЕНТОВ ==========
    initAlerts();       // Инициализировать уведомления
    initTooltips();     // Инициализировать подсказки
    initConfirmDialogs(); // Инициализировать диалоги подтверждения
});

/* ===================== 1. АВТОЗАКРЫТИЕ УВЕДОМЛЕНИЙ (ALERTS) ===================== */
// Уведомления об ошибке/успехе автоматически закрываются через 5 секунд

function initAlerts() {
    // Найти все элементы с классом 'alert'
    const alerts = document.querySelectorAll('.alert');
    // querySelectorAll = найти ВСЕ элементы с этим селектором
    
    // Для каждого уведомления:
    alerts.forEach(alert => {
        // setTimeout = выполнить функцию через N миллисекунд
        // 5000 миллисекунд = 5 секунд
        setTimeout(() => {
            // Создать объект уведомления Bootstrap
            const bsAlert = new bootstrap.Alert(alert);
            // .close() = закрыть уведомление с анимацией
            bsAlert.close();
        }, 5000);
    });
}

/* ===================== 2. ИНИЦИАЛИЗАЦИЯ ПОДСКАЗОК (TOOLTIPS) ===================== */
// Подсказки при наведении мышки на элементы

function initTooltips() {
    // Найти все элементы с атрибутом data-bs-toggle="tooltip"
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    
    // Для каждого элемента создать Bootstrap tooltip
    tooltipTriggerList.map(tooltipTriggerEl => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/* ===================== 3. ДИАЛОГИ ПОДТВЕРЖДЕНИЯ ===================== */
// Спрашивать "Вы уверены?" перед опасными действиями (удаление и т.д.)

function initConfirmDialogs() {
    // Найти все ссылки с классом 'confirm-delete'
    const deleteButtons = document.querySelectorAll('a.confirm-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Если пользователь нажимает на кнопку
            
            // Показать диалог "Вы уверены?"
            if (!confirm('⚠️ Вы уверены? Это действие нельзя отменить!')) {
                // Если ответил "Нет"
                e.preventDefault(); // Не переходить по ссылке
            }
        });
    });
}

/* ===================== 4. ВАЛИДАЦИЯ ФОРМ ===================== */
// Проверять, что все необходимые поля заполнены перед отправкой

function validateForm(formElement) {
    // Получить все поля формы
    const fields = formElement.querySelectorAll('[required]');
    // [required] = поля с атрибутом required
    
    let isValid = true;  // Сначала предположим, что всё хорошо
    
    fields.forEach(field => {
        // Для каждого обязательного поля:
        
        if (field.value.trim() === '') {
            // Если поле пусто
            
            // Добавить красный класс ошибки
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            // Если поле заполнено
            
            // Убрать класс ошибки
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;  // Вернуть результат
}

/* ===================== 5. ОТПРАВКА ФОРМ ЧЕРЕЗ AJAX ===================== */
// Отправлять данные БЕЗ перезагрузки страницы

function submitFormAjax(formElement) {
    // Получить данные формы
    const formData = new FormData(formElement);
    // FormData = автоматически собрать все поля формы
    
    // Отправить на сервер
    fetch(formElement.action, {
        // fetch = отправить запрос на URL
        // formElement.action = куда отправлять (атрибут action в form)
        
        method: formElement.method || 'POST',  // POST = защищённо
        body: formData,                        // Данные формы
        headers: {
            'X-CSRFToken': getCsrfToken()  // Токен безопасности
        }
    })
    .then(response => response.json())  // Ответ как JSON
    .then(data => {
        // Если сервер ответил успешно
        
        if (data.success) {
            // Показать успешное уведомление
            showNotification('✅ ' + data.message, 'success');
            
            // Очистить форму
            formElement.reset();
            
            // Перезагрузить страницу через 1.5 секунды
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            // Если ошибка на сервере
            showNotification('❌ ' + data.message, 'danger');
        }
    })
    .catch(error => {
        // Если ошибка сети
        console.error('Ошибка:', error);
        showNotification('❌ Ошибка сети. Попробуйте позже.', 'danger');
    });
}

/* ===================== 6. ПОКАЗАТЬ УВЕДОМЛЕНИЕ (TOAST) ===================== */
// Красивое всплывающее уведомление в углу экрана

function showNotification(message, type = 'info') {
    // message = текст уведомления
    // type = тип (success, danger, info, warning)
    
    // Создать HTML для уведомления
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type}" role="alert">
            <!-- bg-${type} = цвет в зависимости от типа -->
            
            <div class="d-flex">
                <div class="toast-body">
                    ${message}  <!-- Вставить текст сообщения -->
                </div>
                <!-- Кнопка закрыть -->
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Найти или создать контейнер для уведомлений
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        // Если контейнера нет, создать его
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        // position-fixed = на месте при скролле
        // bottom-0 end-0 = правый нижний угол
        
        document.body.appendChild(toastContainer);
    }
    
    // Добавить уведомление в контейнер
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Создать Bootstrap toast объект и показать
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Удалить уведомление из DOM через 5 секунд
    setTimeout(() => {
        toastElement.remove();
    }, 5000);
}

/* ===================== 7. ПОЛУЧИТЬ CSRF ТОКЕН ===================== */
// CSRF токен нужен для безопасности при отправке данных

function getCsrfToken() {
    // Способ 1: из meta тега (если есть в HTML)
    let token = document.querySelector('meta[name="csrf-token"]');
    if (token) return token.getAttribute('content');
    
    // Способ 2: из скрытого input (обычно в формах Django)
    token = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (token) return token.value;
    
    // Способ 3: из куки
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1] || '';
}

/* ===================== 8. ФОРМАТИРОВАНИЕ ДАТЫ И ВРЕМЕНИ ===================== */
// Преобразовать дату в читаемый формат

function formatDateTime(dateString) {
    // dateString = строка с датой (например "2025-12-18T14:30:00")
    
    // Создать объект Date
    const date = new Date(dateString);
    
    // Форматировать по-русски
    return date.toLocaleString('ru-RU', {
        year: 'numeric',        // 2025
        month: '2-digit',       // 12
        day: '2-digit',         // 18
        hour: '2-digit',        // 14
        minute: '2-digit'       // 30
    });
    // Результат: 18.12.2025, 14:30
}

/* ===================== 9. ЗАГРУЗКА ДАННЫХ С СЕРВЕРА (AJAX) ===================== */
// Получить данные без перезагрузки страницы

function apiCall(url, method = 'GET', data = null) {
    // url = адрес на сервере
    // method = GET (получить) или POST (отправить)
    // data = данные для отправки (JSON)
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',  // Отправляем JSON
            'X-CSRFToken': getCsrfToken()        // Токен безопасности
        }
    };
    
    // Если есть данные для отправки, добавить в body
    if (data) {
        options.body = JSON.stringify(data);  // Преобразовать в JSON
    }
    
    // Отправить запрос
    return fetch(url, options)
        .then(r => {
            // Проверить, успешный ли ответ
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();  // Преобразовать в JSON
        })
        .catch(error => {
            console.error('Ошибка API:', error);
            throw error;
        });
}

/* ===================== 10. ДИНАМИЧЕСКОЕ СКРЫТИЕ/ПОКАЗ ЭЛЕМЕНТОВ ===================== */
// Показывать/скрывать элементы при клике

function toggleElement(selector) {
    // selector = селектор элемента (например ".hidden-menu")
    
    const element = document.querySelector(selector);
    if (!element) return;
    
    // toggle = добавить класс, если его нет, убрать, если есть
    element.classList.toggle('hidden');
    
    // Анимация
    if (element.classList.contains('hidden')) {
        element.style.opacity = '0';
    } else {
        element.style.opacity = '1';
    }
}

/* ===================== 11. ФИЛЬТРАЦИЯ ТАБЛИЦЫ ===================== */
// Фильтровать строки таблицы по введённому тексту

function filterTable(inputSelector, tableSelector) {
    // inputSelector = селектор поля поиска (например "#search-input")
    // tableSelector = селектор таблицы (например "#data-table")
    
    const input = document.querySelector(inputSelector);
    const table = document.querySelector(tableSelector);
    
    if (!input || !table) return;
    
    // При вводе текста
    input.addEventListener('keyup', function() {
        const searchText = this.value.toLowerCase();  // Текст в нижнем регистре
        
        // Найти все строки таблицы
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            // Получить текст строки
            const text = row.textContent.toLowerCase();
            
            // Если текст совпадает с поиском - показать, иначе скрыть
            row.style.display = text.includes(searchText) ? '' : 'none';
        });
    });
}

/* ===================== 12. ПОДСЧЁТ СИМВОЛОВ В TEXTAREA ===================== */
// Показывать, сколько символов написано

function initCharCounter(textareaSelector, counterSelector) {
    // textareaSelector = селектор поля ввода (например "textarea")
    // counterSelector = селектор для счётчика (например ".char-count")
    
    const textarea = document.querySelector(textareaSelector);
    const counter = document.querySelector(counterSelector);
    
    if (!textarea || !counter) return;
    
    // При вводе текста
    textarea.addEventListener('input', function() {
        const count = this.value.length;  // Количество символов
        const maxCount = this.maxLength || 500;  // Максимум (если установлено)
        
        // Обновить счётчик
        counter.textContent = `${count}/${maxCount}`;
        
        // Если достигнут лимит
        if (count >= maxCount) {
            counter.style.color = '#dc3545';  // Красный
        } else if (count > maxCount * 0.8) {
            counter.style.color = '#ffc107';  // Жёлтый
        } else {
            counter.style.color = '#6c757d';  // Серый
        }
    });
}

/* ===================== 13. ОБРАБОТКА КЛАВИАТУРЫ ===================== */
// Выполнить действие при нажатии определённой клавиши

document.addEventListener('keydown', function(e) {
    // Нажата Escape - закрыть модальные окна
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
    
    // Нажата Ctrl+S - сохранить (предотвратить сохранение браузером)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        // Здесь можно добавить свой код сохранения
        showNotification('💾 Сохранение...', 'info');
    }
});

/* ===================== 14. ЗАГРУЗКА ФАЙЛОВ С PREVIEW ===================== */
// Показывать превью изображения перед загрузкой

function initImagePreview(inputSelector, previewSelector) {
    // inputSelector = селектор input[type="file"]
    // previewSelector = селектор элемента для превью
    
    const input = document.querySelector(inputSelector);
    const preview = document.querySelector(previewSelector);
    
    if (!input || !preview) return;
    
    input.addEventListener('change', function() {
        // Если файл выбран
        if (this.files && this.files[0]) {
            const reader = new FileReader();  // Читать файл
            
            reader.onload = function(e) {
                // Когда файл загружен
                preview.src = e.target.result;  // Показать превью
                preview.style.display = 'block';
            };
            
            reader.readAsDataURL(this.files[0]);  // Читать файл как изображение
        }
    });
}

/* ===================== 15. УТИЛИТЫ ===================== */

// Функция логирования (более информативно, чем console.log)
function log(message, data = null) {
    if (data) {
        console.log(`📌 ${message}:`, data);
    } else {
        console.log(`📌 ${message}`);
    }
}

// Функция для задержки (используется с async/await)
async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Функция для скрытия элемента
function hide(selector) {
    document.querySelector(selector)?.classList.add('d-none');
}

// Функция для показа элемента
function show(selector) {
    document.querySelector(selector)?.classList.remove('d-none');
}

// Функция для переключения видимости
function toggle(selector) {
    document.querySelector(selector)?.classList.toggle('d-none');
}
