import os
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")

YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')

ADMIN_ID = os.getenv('ADMIN_ID')
if not ADMIN_ID:
    raise ValueError("❌ ADMIN_ID не найден в .env файле!")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Загружаем данные бизнеса из JSON
def load_business_data():
    with open('business_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

BUSINESS_DATA = load_business_data()
