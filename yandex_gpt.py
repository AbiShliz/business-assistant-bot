"""
Модуль для работы с YandexGPT API
Содержит функции для отправки запросов и генерации ответов
"""

import aiohttp
import logging
import json
from typing import Optional

# Настройка логирования
logger = logging.getLogger(__name__)

# URL для YandexGPT API
YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

async def ask_yandex_gpt(
    prompt: str, 
    temperature: float = 0.6,
    max_tokens: int = 500,
    system_prompt: Optional[str] = None
) -> str:
    """
    Отправляет запрос к YandexGPT и возвращает ответ
    
    Аргументы:
        prompt: текст запроса пользователя
        temperature: температура генерации (0.0 - 1.0)
        max_tokens: максимальное количество токенов в ответе
        system_prompt: системный промпт (если нужен)
    
    Возвращает:
        str: ответ от нейросети или сообщение об ошибке
    """
    
    # Импортируем конфиг внутри функции, чтобы избежать циклических импортов
    from config import YANDEX_API_KEY, YANDEX_FOLDER_ID
    
    # Проверяем, что ключи не пустые
    if not YANDEX_API_KEY:
        logger.error("YANDEX_API_KEY is empty!")
        return "❌ Ошибка: не настроен API-ключ YandexGPT. Проверьте переменные окружения."
    
    if not YANDEX_FOLDER_ID:
        logger.error("YANDEX_FOLDER_ID is empty!")
        return "❌ Ошибка: не указан Folder ID. Проверьте переменные окружения."
    
    # Убираем возможные пробелы в начале и конце
    api_key = YANDEX_API_KEY.strip()
    folder_id = YANDEX_FOLDER_ID.strip()
    
    logger.info(f"Using folder_id: {folder_id}")
    logger.info(f"API key length: {len(api_key)}")
    
    # Формируем modelUri
    model_uri = f"gpt://{folder_id}/yandexgpt-lite"
    logger.info(f"Model URI: {model_uri}")
    
    # Заголовки запроса
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }
    
    # Формируем сообщения
    messages = []
    
    # Системный промпт по умолчанию для бизнес-ассистента
    if system_prompt is None:
        system_prompt = (
            "Ты вежливый и дружелюбный помощник для клиентов салона красоты. "
            "Отвечай кратко, по делу, но приветливо. "
            "Если не знаешь ответа, предложи связаться с администратором."
        )
    
    messages.append({
        "role": "system",
        "text": system_prompt
    })
    
    messages.append({
        "role": "user",
        "text": prompt
    })
    
    # Тело запроса
    data = {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": messages
    }
    
    logger.info(f"Sending request to YandexGPT with {len(messages)} messages")
    
    try:
        # Отправляем запрос
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_URL, headers=headers, json=data) as response:
                
                # Логируем статус ответа
                logger.info(f"Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    logger.info("Successfully got response from YandexGPT")
                    
                    # Извлекаем ответ
                    try:
                        answer = result['result']['alternatives'][0]['message']['text']
                        return answer.strip()
                    except (KeyError, IndexError) as e:
                        logger.error(f"Failed to parse response: {e}")
                        logger.error(f"Response structure: {json.dumps(result, indent=2)[:500]}")
                        return "❌ Ошибка при обработке ответа от нейросети."
                
                else:
                    # Подробный вывод ошибки
                    error_text = await response.text()
                    logger.error(f"YandexGPT API error: {response.status}")
                    logger.error(f"Error details: {error_text[:500]}")
                    
                    # Понятное сообщение для пользователя
                    if response.status == 403:
                        return "❌ Ошибка доступа к YandexGPT. Проверьте права сервисного аккаунта (роль ai.languageModels.user)."
                    elif response.status == 401:
                        return "❌ Ошибка авторизации. Неверный API-ключ."
                    elif response.status == 429:
                        return "❌ Превышен лимит запросов к YandexGPT. Попробуйте позже."
                    elif response.status == 400:
                        return f"❌ Неверный запрос к API. Проверьте Folder ID и модель. Детали: {error_text[:200]}"
                    else:
                        return f"❌ Ошибка YandexGPT (код {response.status}). Попробуйте позже."
    
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Connection error: {e}")
        return "❌ Ошибка соединения с сервером YandexGPT. Проверьте интернет."
    
    except aiohttp.ClientError as e:
        logger.error(f"Network error: {e}")
        return "❌ Ошибка сети при обращении к YandexGPT."
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return f"❌ Непредвиденная ошибка: {str(e)}"

async def generate_welcome(user_name: str) -> str:
    """
    Генерирует персонализированное приветствие для клиента
    
    Аргументы:
        user_name: имя пользователя
    
    Возвращает:
        str: тёплое приветствие
    """
    prompt = (
        f"Придумай короткое, тёплое приветствие для клиента {user_name}, "
        f"который только что зашёл в бота салона красоты. "
        f"Максимум 2 предложения. Будь дружелюбным."
    )
    return await ask_yandex_gpt(prompt, temperature=0.8, max_tokens=100)

async def generate_response(user_message: str, context: str = "") -> str:
    """
    Упрощённая функция для ответов на вопросы клиентов
    
    Аргументы:
        user_message: сообщение пользователя
        context: дополнительный контекст (например, информация о салоне)
    
    Возвращает:
        str: ответ от нейросети
    """
    prompt = f"""
Контекст (информация о салоне):
{context}

Вопрос клиента: {user_message}

Ответь вежливо и полезно. Если вопрос не относится к услугам салона, 
предложи связаться с администратором.
"""
    return await ask_yandex_gpt(prompt, temperature=0.7)