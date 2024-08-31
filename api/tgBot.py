import logging
import telebot
import os
import numpy as np
from moviepy.editor import VideoFileClip, vfx, CompositeVideoClip, ImageClip
import cv2
from PIL import Image
from flask import Flask, request, abort

TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

input_dir = os.path.abspath('videos')
output_dir = os.path.abspath('ready')
overlay_image = os.path.abspath('overlay.png')

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Отправь мне видеофайл для обработки.')

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        filename = file_info.file_path.split('/')[-1]
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Download the video
        downloaded_file = bot.download_file(file_info.file_path)
        with open(input_path, 'wb') as f:
            f.write(downloaded_file)

        bot.send_message(message.chat.id, f'Принял видео: {filename}')

        success, result_message = process_video(input_path, output_path, overlay_image)

        if success:
            with open(output_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
            # Clean up the directories
            clean_directory(input_dir)
            clean_directory(output_dir)
        else:
            bot.send_message(message.chat.id, f'Ошибка при обработке видео: {result_message}')

    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при загрузке/обработке видео: {e}')

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://your-vercel-domain.vercel.app/' + TOKEN)
    return "Webhook set!", 200

def process_video(input_path, output_path, overlay_image_path):
    # Your video processing code here...
    pass

def clean_directory(directory):
    # Your clean directory code here...
    pass

if __name__ == "__main__":
    app.run()
