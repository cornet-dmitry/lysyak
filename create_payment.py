import requests
import base64
import uuid


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