import telebot
import config
import main
import tracker
import analyzer
import video_maker
import shutil
import os
from datetime import datetime
import background_extractor

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(message.content_type)
    bot.reply_to(message, "Howdy, how are you doing?")


# @bot.message_handler(commands=['video'])
# def send_welcome(message):
#     with open('tests\\2020_11_14_18_18_05\\output.avi', 'rb') as output:
#         bot.send_document(message.chat.id, output, reply_to_message_id=message.chat.id)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.content_type)
    bot.reply_to(message, message.text)


# # Handles all sent documents and audio files
# @bot.message_handler(content_types=['document', 'audio'])
# def handle_docs_audio(message):
#     print(message.content_type)


@bot.message_handler(content_types=['document'])
def get_video(message):
    try:
        file_name = message.document.file_name
        file_id_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        CURRENT_TEST_FOLDER = os.path.join('tests', timestamp)

        if not os.path.exists(CURRENT_TEST_FOLDER):
            os.mkdir(CURRENT_TEST_FOLDER)

        INPUT_VIDEO = os.path.join(CURRENT_TEST_FOLDER, file_name)

        with open(INPUT_VIDEO, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Initialize required paths
        TRACKED_DATA = os.path.join(CURRENT_TEST_FOLDER, 'tracked_data.json')
        ANALYZED_DATA = os.path.join(CURRENT_TEST_FOLDER, 'analyzed_data.json')
        CROPPED_IMAGES_FOLDER = os.path.join(CURRENT_TEST_FOLDER, 'cropped_images')

        if not os.path.exists(CROPPED_IMAGES_FOLDER):
            os.mkdir(CROPPED_IMAGES_FOLDER)

        BACKGROUND = os.path.join(CURRENT_TEST_FOLDER, 'background.png')
        OUTPUT_VIDEO_FILENAME = f'{os.path.splitext(file_name)[0]}_summary.avi'
        OUTPUT_VIDEO = os.path.join(CURRENT_TEST_FOLDER, OUTPUT_VIDEO_FILENAME)

        bot.send_message(message.chat.id, 'Tracking objects...')
        tracker.track_video(INPUT_VIDEO, TRACKED_DATA, CROPPED_IMAGES_FOLDER)

        bot.send_message(message.chat.id, 'Extracting the background...')
        background_extractor.extract(INPUT_VIDEO, BACKGROUND, CURRENT_TEST_FOLDER)

        bot.send_message(message.chat.id, 'Analyzing tracked data...')
        analyzer.analyze_json(TRACKED_DATA, ANALYZED_DATA)

        bot.send_message(message.chat.id, 'Making result video...')
        video_maker.make(CROPPED_IMAGES_FOLDER, ANALYZED_DATA, BACKGROUND, OUTPUT_VIDEO)

        with open(OUTPUT_VIDEO, 'rb') as output:
            bot.send_document(message.chat.id, output)

        # Move and delete redundant files and folders
        for file in os.listdir(CROPPED_IMAGES_FOLDER):
            os.remove(os.path.join(CROPPED_IMAGES_FOLDER, file))

        os.rmdir(CROPPED_IMAGES_FOLDER)
        os.remove(BACKGROUND)
        os.remove(TRACKED_DATA)
        os.remove(ANALYZED_DATA)
        os.remove(INPUT_VIDEO)
        os.remove(OUTPUT_VIDEO)

        print('Done')

    except Exception as ex:
        bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


bot.polling()
