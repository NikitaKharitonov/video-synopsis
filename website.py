from flask import Flask, url_for, render_template, request, send_from_directory, session, redirect
import cv2
import numpy
import shutil
import os
import ntpath
from datetime import datetime

import config
import summarizer

app = Flask(__name__)
app.secret_key = config.secret_key


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
    input_video_file_name = str(video.filename)
    videos_dirname = 'videos'
    current_video_dirname = str(datetime.now().time()).replace(':', '.')
    input_video_dir_path = os.path.join(videos_dirname, current_video_dirname)
    while os.path.exists(input_video_dir_path):
        input_video_dir_path += '+'
    os.mkdir(input_video_dir_path)
    input_video_file_path = os.path.join(input_video_dir_path, input_video_file_name)
    video.save(input_video_file_path)

    output_video_file_path = summarizer.summarize(input_video_file_path)

    return send_from_directory(ntpath.dirname(output_video_file_path), filename=ntpath.basename(output_video_file_path), as_attachment=True)


@app.route('/download')
def download():
    return render_template('download.html')


if __name__ == '__main__':
    app.port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run()