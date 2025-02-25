import requests
import base64
import uuid

from datetime import datetime, timedelta


# Данные от ЮKassa
shop_id = '1040120'
secret_key = 'test_xAjiKWfp_I7dtKWUr787qUaWHjCcRhAwcBzwfTqLt0M'
auth = base64.b64encode(f"{shop_id}:{secret_key}".encode()).decode()

# Данные сайта
return_url = "http://127.0.0.1:5000/"


def get_payment_url(amount, email, payment_method):
    # payment_method = "bank_card"  # или "sbp" для СБП

    data = {}

    if payment_method == "sbp":
        pass
    elif payment_method == "sberpay":
        pass
    elif payment_method == "tbank":
        pass
    elif payment_method == "visa":
        
        # Формируем данные для ЮKassa
        data = {
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "description": "Пожертвование для Даши",
            "metadata": {
                "email": email
            }
        }

    elif payment_method == "iomoney":
        pass
    elif payment_method == "usdt":
        pass
    
    
    if data is not None:
         # Отправка запроса в ЮKassa
        response = requests.post(
            "https://api.yookassa.ru/v3/payments",
            headers={
                "Idempotence-Key": str(uuid.uuid4()),
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth}"
            },
            json=data
        )

        # Возвращаем ссылку для оплаты
        payment_url = response.json()['confirmation']['confirmation_url']
        return payment_url
    else:
        return ValueError("Что-то пошло не так...")
    

def get_all_payment():
    # Параметры запроса
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # За последние 30 дней

    # Запрос списка платежей
    response = requests.get(
        "https://api.yookassa.ru/v3/payments",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        },
        params={
            "created_at.gte": start_date.isoformat() + "Z",
            "created_at.lt": end_date.isoformat() + "Z",
            "limit": 100  # Максимальное количество платежей за один запрос
        }
    )

    # Обработка ответа
    if response.status_code == 200:
        payments = response.json()['items']
        total_amount = 0

        for payment in payments:
            if payment['status'] == 'succeeded':
                total_amount += float(payment['amount']['value'])
        
        return total_amount
    else:
        return None