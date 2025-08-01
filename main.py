
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import logging
import os

print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))  # Для отладки
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_data = {}

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("Рассчитать ОСАГО"))

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Здравствуйте! Нажмите кнопку для расчёта ОСАГО:", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "Рассчитать ОСАГО")
async def ask_region(msg: types.Message):
    user_data[msg.from_user.id] = {"step": "region"}
    await msg.answer("Введите ваш регион (например: Москва):")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "region")
async def handle_region(msg: types.Message):
    user_data[msg.from_user.id]["region"] = msg.text
    user_data[msg.from_user.id]["step"] = "power"
    await msg.answer("Введите мощность автомобиля в л.с.:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "power")
async def handle_power(msg: types.Message):
    try:
        power = int(msg.text)
        user_data[msg.from_user.id]["power"] = power
        user_data[msg.from_user.id]["step"] = "age"
        await msg.answer("Введите возраст водителя:")
    except ValueError:
        await msg.answer("Пожалуйста, введите число (мощность в л.с.)")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "age")
async def handle_age(msg: types.Message):
    try:
        age = int(msg.text)
        user_data[msg.from_user.id]["age"] = age
        user_data[msg.from_user.id]["step"] = "kbm"
        await msg.answer("Введите КБМ (например, 0.85 — если без аварий):")
    except ValueError:
        await msg.answer("Пожалуйста, введите возраст числом.")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "kbm")
async def handle_kbm(msg: types.Message):
    try:
        kbm = float(msg.text.replace(",", "."))
        user_data[msg.from_user.id]["kbm"] = kbm

        # Пример расчёта
        base = 5000
        result = base * user_data[msg.from_user.id]["kbm"]
        await msg.answer(f"Примерная стоимость ОСАГО: {int(result)} ₽")
    except ValueError:
        await msg.answer("Введите корректное значение КБМ.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
