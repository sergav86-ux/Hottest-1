import os
import io
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import speech_recognition as sr
from pydub import AudioSegment


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

@dp.message(lambda message: message.voice)
async def handle_voice(message: types.Message):
    # Скачиваем голосовое сообщение (оно придет в формате .ogg)
    file_info = await bot.get_file(message.voice.file_id)
    ogg_path = "voice.ogg"
    wav_path = "voice.wav"
    
    await bot.download_file(file_info.file_path, ogg_path)
    
    try:
        # Конвертируем OGG в WAV с помощью pydub
        audio = AudioSegment.from_file(ogg_path, format="ogg")
        audio.export(wav_path, format="wav")
        
        # Распознаем текст
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="ru-RU")
            await message.reply(f"Распознанный текст:\n{text}")
            
    except Exception as e:
        await message.reply("Не удалось распознать речь. Возможно, аудио слишком тихое или формат не поддерживается сервером.")
    finally:
        # Удаляем временные файлы, чтобы не забивать память сервера
        if os.path.exists(ogg_path): os.remove(ogg_path)
        if os.path.exists(wav_path): os.remove(wav_path)

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
    
