import os
import io
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import speech_recognition as sr

from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

API_TOKEN = '8923805769:AAGdnmjaebZIiarRT1JtosNnH7tOhb21NtI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
recognizer = sr.Recognizer()

@dp.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне голосовое сообщение, и я превращу его в текст.")

@dp.message()
async def handle_voice(message: types.Message):
    if not message.voice:
        return

    status_msg = await message.reply("Скачиваю аудио и расшифровываю... Подождите.")
    
    try:
        file_id = message.voice.file_id
        file_info = await bot.get_file(file_id)
        
        file_on_disk = await bot.download_file(file_info.file_path)
        audio_stream = io.BytesIO(file_on_disk.read())

        with sr.AudioFile(audio_stream) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            
        await status_msg.edit_text(f"Вот ваш текст:\n\n{text}")
        
    except Exception as e:
        await status_msg.edit_text("Не удалось распознать речь. Возможно, аудио слишком тихое или формат не поддерживается сервером.")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
    
