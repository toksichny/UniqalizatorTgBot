import logging
import telebot
import os
import numpy as np
from moviepy.editor import VideoFileClip, vfx, CompositeVideoClip, ImageClip
import cv2
from PIL import Image
from background import keep_alive 

keep_alive()
# Telegram bot token (replace with your bot token)
TOKEN = '7343096071:AAEMO_EnoJF5Rkg-M9TshJLXffTMHYVZMrw'

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Define directories
input_dir = os.path.abspath('videos')
output_dir = os.path.abspath('ready')
overlay_image = os.path.abspath('overlay.png')  # Specify your overlay image path

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

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
            #os.remove(output_path)  # Delete processed video after sending
        else:
            bot.send_message(message.chat.id, f'Ошибка при обработке видео: {result_message}')

    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при загрузке/обработке видео: {e}')

def process_video(input_path, output_path, overlay_image_path):
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".mp4"):
            video_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                video = VideoFileClip(video_path)
                print(f"Video loaded: {input_path}")
            except Exception as e:
                print(f"Error loading video {input_path}: {e}")
                return

            try:
                # Copy and resize video (if needed, else this can be removed)
                video = video.copy().resize((video.w, video.h))
                print(f"Video resize")
            except Exception as e:
                print(f"Error resize video: {e}")
                return

            try:
                # Remove audio
                video = video.without_audio()
                print(f"Audio Remove")
            except Exception as e:
                print(f"Error Audio Remove: {e}")
                return

            # Apply effects
            try:
                video = video.fx(vfx.speedx, 0.9)
                print(f"Playback speed adjusted")
            except Exception as e:
                print(f"Error adjusting playback speed: {e}")
                return

            try:
                video = video.fx(vfx.mirror_x)
                print(f"Video mirrored")
            except Exception as e:
                print(f"Error mirroring video: {e}")
                return
            try:
                video = video.rotate(1)
                print("Video rotated")
            except Exception as e:
                print(f"Error rotating video: {e}")
                return
            try:
                # Process overlay image
                overlay_image = Image.open(overlay_image_path)
                overlay_array = np.array(overlay_image)
                overlay_clip = ImageClip(overlay_array, ismask=False)
                overlay_clip = overlay_clip.resize(video.size)
                overlay_clip = overlay_clip.set_duration(video.duration)
                print("Overlay applied")
            except Exception as e:
                print(f"Error applying overlay: {e}")
                return
            '''
            try:
                # Create a blurred background video
                def blur_frame(frame):
                    return cv2.GaussianBlur(frame, (51, 51), 0)

                blurred_background = video.fl_image(blur_frame).resize(1.2)
                print("Background blurred and resized")
            except Exception as e:
                return False, f"Error creating blurred background: {e}"
            '''
            try:
                # Create final clip with overlay
                final_clip = CompositeVideoClip([video, overlay_clip])
            except Exception as e:
                print(f"Error Create final clip with overlay : {e}")
                return

            try:
                # Write final video to output directory, removing metadata by setting a blank metadata dictionary
                final_clip.write_videofile(output_path, codec='libx264', remove_temp=True, 
                                        write_logfile=False, ffmpeg_params=['-map_metadata', '-1'])
                print(f"Video written to {output_path}")
                return True, "Success"
            except Exception as e:
                print(f"Error writing video and delete metadata {output_path}: {e}")
                return
def clean_directory(directory):
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
                logger.info(f'File removed: {file_path}')
            except Exception as e:
                logger.error(f'Error cleaning file {file_path}: {e}')
    except Exception as e:
        logger.error(f'Error accessing directory {directory}: {e}')

if __name__ == '__main__':
    bot.polling(none_stop=True)
