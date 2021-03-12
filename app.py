from flask import Flask, url_for, render_template, request, send_from_directory, session, redirect
import cv2
import numpy
import shutil
import os
from datetime import datetime


import yolo_deepsort_detector
import background_extractor
import analyzer
import video_maker
import config


app = Flask(__name__)
app.secret_key = config.secret_key
# app.port = int(os.environ.get('PORT', 5000))
# app.debug = True
# app.host = '0.0.0.0'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


# @app.route('/history')
# def history():
#     if 'videos' not in session:
#         session['videos'] = []
#     return render_template('history.html', videos=session['videos'])


# @app.route('/login')
# def login():
#     return render_template('login.html')


# @app.route('/signup')
# def signup():
#     return render_template('signup.html')


@app.route('/getvideo', methods=['GET'])
def getvideo():
    index = request.args.get('index') 
    if index is None:
        video = session['current_video']
        return send_from_directory(video['directory'], filename=video['filename'], as_attachment=True)
    video = session['videos'][int(index) - 1]
    return send_from_directory(video['directory'], filename=video['filename'], as_attachment=True)


CROPPED_IMAGES_FOLDER_NAME = 'cropped_images'
TRACKED_DATA_FILE_NAME = 'tracked_data.json'
ANALYZED_DATA_FILE_NAME = 'analyzed_data.json'
BACKGROUND_FILE_NAME = 'background.png'
TESTS_DIR_NAME = 'tests'
TIMESTAMP_FORMAT = "%Y_%m_%d_%H_%M_%S"


@app.route('/submit', methods=['POST'])
def submit():
    video = request.files.get('video', '')
    
    if not os.path.exists(TESTS_DIR_NAME):
        os.mkdir(TESTS_DIR_NAME)
    
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    test_dir_name = os.path.join(TESTS_DIR_NAME, timestamp)

    while os.path.exists(test_dir_name):
        test_dir_name += '+'

    os.mkdir(test_dir_name)

    input_video_file_name = str(video.filename)

    input_video_file_path = os.path.join(test_dir_name, input_video_file_name)
    tracked_data_file_path = os.path.join(test_dir_name, TRACKED_DATA_FILE_NAME)
    analyzed_data_file_path = os.path.join(test_dir_name, ANALYZED_DATA_FILE_NAME)
    cropped_images_dir_name = os.path.join(test_dir_name, CROPPED_IMAGES_FOLDER_NAME)

    if not os.path.exists(cropped_images_dir_name):
        os.mkdir(cropped_images_dir_name)

    background_file_path = os.path.join(test_dir_name, BACKGROUND_FILE_NAME)
    output_video_file_name = input_video_file_name[:input_video_file_name.rfind('.')] + "_Synopsis.avi"
    output_video_file_path = os.path.join(test_dir_name, output_video_file_name)

    video.save(input_video_file_path)

    print('Tracking objects...')
    yolo_deepsort_detector.track_video(input_video_file_path, tracked_data_file_path, cropped_images_dir_name)

    print('Extracting the background...')
    background_extractor.extract(input_video_file_path, background_file_path, test_dir_name)

    print('Analyzing tracked data...')
    analyzer.analyze_json(tracked_data_file_path, analyzed_data_file_path)

    print('Making result video...')
    video_maker.make(cropped_images_dir_name, analyzed_data_file_path, background_file_path, output_video_file_path)
    # video.save(output_video_file_path)
    print('Output video saved to {}'.format(output_video_file_path))

    for file in os.listdir(cropped_images_dir_name):
        os.remove(os.path.join(cropped_images_dir_name, file))

    if os.path.exists(cropped_images_dir_name):
        os.rmdir(cropped_images_dir_name)
    if os.path.exists(background_file_path):
        os.remove(background_file_path)
    if os.path.exists(tracked_data_file_path):
        os.remove(tracked_data_file_path)
    if os.path.exists(analyzed_data_file_path):
        os.remove(analyzed_data_file_path)
    if os.path.exists(input_video_file_path):
        os.remove(input_video_file_path)

    print('Done')

    return send_from_directory(test_dir_name, filename=output_video_file_name, as_attachment=True)


@app.route('/download')
def download():
    return render_template('download.html')


if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 5000)))