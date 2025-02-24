from flask import Flask, render_template, url_for, request, redirect, abort, flash
from flask_wtf.csrf import CSRFProtect

import smtplib
from email.mime.text import MIMEText
from email.header import Header

import secrets

from create_payment import get_payment_url


app = Flask(__name__)
app.secret_key = "3b9f8a7c5d6e4f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0"

csrf = CSRFProtect(app)


@app.route('/')
def index():
    return render_template('index.html')


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

    # Логика отправки письма

    login = "test-dzen-channel@yandex.ru"
    password = "sk2-fQJ-6pa-Rsa"
    finish_email = "cornet.dmitry28@yandex.ru"

    msg = MIMEText(f'{message}', 'plain', 'utf-8')
    msg['Subject'] = Header(f'Обращение от пользователя {name}', 'utf-8')
    msg['From'] = login
    msg['To'] = finish_email

    s = smtplib.SMTP('smtp.yandex.ru', 587, timeout=10)

    try:
        s.starttls()
        s.login(login, password)
        s.sendmail(msg['From'], msg['To'], msg.as_string())

        flash('Ваше сообщение отправлено!', 'success')
    except Exception as e:
        print(e)
        flash(f'Ошибка при отправке сообщения: {str(e)}', 'error')
        abort(500)

    return redirect('/')

"""
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
"""

if __name__ == "__main__":
    app.run(debug=True)