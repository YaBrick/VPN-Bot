#RuKassa
import requests
import json
import time
import random

token = '' #Your RuKassa Token
order_id = str(int(time.time())) + str(random.randint(10000, 99999))
amount = 300

params = {
    'param1': 'Ваше значение',
    'param2': 'Ваше значение',
    'param3': 'Ваше значение'
}

data = {
    'shop_id': '',  # ID Of your merchant
    'token': token,
    'order_id': order_id,
    'amount': amount,
    'data': json.dumps(params)
}

url = 'https://lk.rukassa.pro/api/v1/create'

# Выполняем HTTP POST-запрос
response = requests.post(url, data=data)

# Проверяем статус код ответа
if response.status_code == 200:
    # Декодируем JSON-ответ
    result = response.json()
    payment_url = result['url']
    print(payment_url)  # Это URL для редиректа на страницу оплаты
else:
    print(f"Ошибка запроса. Код статуса: {response.status_code}")
