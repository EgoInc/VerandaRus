import requests
from django.conf import settings

def send_telegram_message(chat_id, text):
    token = settings.TG_BOT_TOKEN
    if not token:
        print("TG_BOT_TOKEN не настроен")
        return None
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка Telegram: {e}")
        return None