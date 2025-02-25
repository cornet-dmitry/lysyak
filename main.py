from flask import Flask, render_template, url_for, request, redirect, abort, flash, jsonify

from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect

import logging
from yookassa import Configuration, Payment

import requests
import os
from dotenv import load_dotenv

from create_payment import get_payment_url, get_all_payment


# Загружаем переменные из .env
load_dotenv()


app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24).hex()  # Генерация случайного ключа
csrf = CSRFProtect(app)  # Включаем CSRF-защиту для всего приложения

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка Юкассы
Configuration.account_id = os.getenv('SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')


@app.route('/')
def index():
    collected_amount = get_all_payment() + 1899378
    total_amount = 5360526

    return render_template('index.html', total_amount=total_amount, collected_amount=collected_amount)


@app.route('/donation', methods=['POST', 'GET'])
def donation():
    if request.method == 'POST':
        amount = request.form['number-button']
        email = request.form['email-button']
        payment_method = request.form.get('payment_method')  # Получаем метод оплаты
        
        try:
            payment_url = get_payment_url(amount, email, payment_method)

            #  "Ваша почта:" + email + "<br>Метод оплаты:" + payment_method + "<br>Сумма пожертвования: " + amount + "<br>" + payment_link
            return redirect(payment_url)
        except Exception as e:
            abort(500)
    else:
        return redirect('/')


@app.route('/handle-feedback', methods=['POST'])
def handle_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('Все поля обязательны для заполнения', 'error')
        return redirect('/')

    send_tg_message(name, email, message)

    return redirect('/')


def send_tg_message(name, email, message):
    # Замените на ваш токен и ID чата
    TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
    TELEGRAM_CHAT_ID = '709913170'

    # Формируем текст сообщения
    telegram_message = (
        f"Получено новое обращение от {name}\n"
        f"Контакт отправлителя: {email}\n\n"
        f"Текст обращения:\n{message}"
    )

    # URL для отправки сообщения через Telegram Bot API
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

    # Параметры запроса
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': telegram_message
    }

    # Отправляем POST-запрос
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Проверяем, что запрос выполнен успешно
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
        return False
    

@app.route('/webhook', methods=['POST'])
@csrf.exempt  # Отключаем CSRF для этого маршрута
def yookassa_webhook():
    """Обрабатывает уведомления от Юкассы."""
    data = request.json
   
    print("Заголовки запроса:", request.headers)  # Логируем заголовки
    print("Тело запроса:", request.data)  # Логируем сырые данные

    # Логируем полученные данные
    logger.info(f"Получено уведомление от Юкассы: {data}")

    # Проверяем, что это уведомление о платеже
    if 'object' in data and data['object'].get('status') == 'waiting_for_capture':
        payment_id = data['object']['id']

        # Автоподтверждение платежа
        try:
            payment = Payment.capture(payment_id)
            logger.info(f"Платеж {payment_id} подтвержден: {payment}")

            # Отправляем уведомление в Telegram
            amount = payment.amount.value
            currency = payment.amount.currency

            # Извлекаем email из metadata
            metadata = data.get('object', {}).get('metadata', {})
            email = metadata.get('email')

            message = (
                f"✅ Платеж подтвержден!\n"
                f"ID платежа: {payment_id}\n"
                f"Сумма: {amount} {currency}"
            )
            send_tg_message("СЛУЖЕБНОЕ", email, message)

        except Exception as e:
            logger.error(f"Ошибка при подтверждении платежа {payment_id}: {e}")
            send_tg_message(f"❌ Ошибка при подтверждении платежа {payment_id}: {e}")

    return jsonify({'status': 'ok'}), 200
    

# Обработчик для ошибки 404 (страница не найдена)
@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        'error.html',
        error_title="Страница не найдена",
        error_message="Запрошенная страница не существует. Проверьте URL или перейдите на главную.",
        error_code=404
    ), 404
    

# Обработчик для ошибки 500 (внутренняя ошибка сервера)
@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        'error.html',
        error_title="Ошибка сервера",
        error_message="Произошла внутренняя ошибка сервера. Пожалуйста, попробуйте позже.",
        error_code=500
    ), 500


# Обработчик для ошибки 400 (неверный запрос)
@app.errorhandler(400)
def bad_request(error):
    return render_template(
        'error.html',
        error_title="Неверный запрос",
        error_message="Ваш запрос не может быть обработан. Проверьте введённые данные.",
        error_code=400
    ), 400


if __name__ == "__main__":
    app.run(debug=True)