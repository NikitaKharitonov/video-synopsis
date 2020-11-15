import os
import ntpath as path
from datetime import datetime

import telebot
from flask import Flask, request

import analyzer
import background_extractor
import tracker
import video_maker
import config

TOKEN = config.token
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name + '! Send me an .avi video file and I will send you its summary')


# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def echo_message(message):
#     bot.reply_to(message, message.text)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://cryptic-inlet-53281.herokuapp.com/' + TOKEN)
    return "!", 200


@bot.message_handler(content_types=['document'])
def get_video(message):
    try:
        file_name = message.document.file_name
        if file_name.split('.')[-1] != 'avi':
            raise Exception('.avi files only!')
        file_id_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        current_test_folder_path = path.join('tests', timestamp)

        if not path.exists(current_test_folder_path):
            os.mkdir(current_test_folder_path)

        input_video_path = path.join(current_test_folder_path, file_name)

        with open(input_video_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Initialize required paths
        tracked_data_path = path.join(current_test_folder_path, 'tracked_data.json')
        analyzed_data_path = path.join(current_test_folder_path, 'analyzed_data.json')
        cropped_images_folder_path = path.join(current_test_folder_path, 'cropped_images')

        if not path.exists(cropped_images_folder_path):
            os.mkdir(cropped_images_folder_path)

        background_path = path.join(current_test_folder_path, 'background.png')
        output_video_filename = f'{path.splitext(file_name)[0]}_summary.avi'
        output_video_path = path.join(current_test_folder_path, output_video_filename)

        bot.send_message(message.chat.id, 'Tracking objects...')
        tracker.track_video(input_video_path, tracked_data_path, cropped_images_folder_path)

        bot.send_message(message.chat.id, 'Extracting the background...')
        background_extractor.extract(input_video_path, background_path, current_test_folder_path)

        bot.send_message(message.chat.id, 'Analyzing tracked data...')
        analyzer.analyze_json(tracked_data_path, analyzed_data_path)

        bot.send_message(message.chat.id, 'Making result video...')
        video_maker.make(cropped_images_folder_path, analyzed_data_path, background_path, output_video_path)

        with open(output_video_path, 'rb') as output:
            bot.send_document(message.chat.id, output)

        # Move and delete redundant files and folders
        for filename in os.listdir(cropped_images_folder_path):
            filepath = path.join(cropped_images_folder_path, filename)
            if path.exists(filepath):
                os.remove(filepath)

        if path.exists(cropped_images_folder_path):
            os.rmdir(cropped_images_folder_path)
        if path.exists(background_path):
            os.remove(background_path)
        if path.exists(tracked_data_path):
            os.remove(tracked_data_path)
        if path.exists(analyzed_data_path):
            os.remove(analyzed_data_path)
        if path.exists(input_video_path):
            os.remove(input_video_path)
        if path.exists(output_video_path):
            os.remove(output_video_path)

    except Exception as ex:
        bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
