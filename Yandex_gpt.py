import aiohttp
import logging
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

async def ask_yandex_gpt(prompt: str, temperature: float = 0.6) -> str:
    """Отправляет запрос к YandexGPT и возвращает ответ"""
    
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": 500
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты вежливый и дружелюбный помощник для клиентов салона красоты. Отвечай кратко, по делу, но приветливо. Если не знаешь ответа, предложи связаться с администратором."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_URL, headers=headers, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    answer = result['result']['alternatives'][0]['message']['text']
                    return answer
                else:
                    error_text = await resp.text()
                    logging.error(f"YandexGPT API error: {resp.status} - {error_text}")
                    return "❌ Извините, техническая ошибка. Попробуйте позже."
    except Exception as e:
        logging.error(f"YandexGPT connection error: {e}")
        return "❌ Не удалось получить ответ. Попробуйте позже."

async def generate_response(user_message: str, context: str = "") -> str:
    """Упрощённая функция для ответов на вопросы"""
    prompt = f"""
Контекст: {context}
Вопрос пользователя: {user_message}

Ответь вежливо и полезно.
"""
    return await ask_yandex_gpt(prompt)

async def generate_welcome(user_name: str) -> str:
    """Генерирует персонализированное приветствие"""
    prompt = f"Придумай короткое, тёплое приветствие для клиента {user_name}, который только что зашёл в бота салона красоты. Максимум 2 предложения."
    return await ask_yandex_gpt(prompt, temperature=0.8)
