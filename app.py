from flask import Flask, url_for, render_template, request, send_from_directory, session, redirect
import cv2
import numpy
import tracker
import analyzer
import video_maker
import shutil
import os
from datetime import datetime
import background_extractor
import yolo_deepsort_detector

app = Flask(__name__)

app.secret_key = b'_fghhkjobve4980klg5'

app.debug = True

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    if 'videos' not in session:
        session['videos'] = []
    return render_template('history.html', videos=session['videos'])

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/getvideo', methods=['GET'])
def getvideo():
    index = request.args.get('index') 
    if index is None:
        video = session['current_video']
        return send_from_directory(video['directory'], filename=video['filename'], as_attachment=True)
    video = session['videos'][int(index) - 1]
    return send_from_directory(video['directory'], filename=video['filename'], as_attachment=True)

@app.route('/submit', methods=['POST'])
def submit():


    myfile = request.files.get('video', '')
    


    video = {
        'name': myfile.filename,
        'datetime': datetime.now()
    }

    #Initialize required paths
    TESTS_FOLDER = 'tests'
    TIMESTAMP_FORMAT = "%Y_%m_%d_%H_%M_%S"

    if not os.path.exists(TESTS_FOLDER):
        os.mkdir(TESTS_FOLDER)

    
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    CURRENT_TEST_FOLDER = os.path.join(TESTS_FOLDER, timestamp)

    while os.path.exists(CURRENT_TEST_FOLDER):
        CURRENT_TEST_FOLDER += '+'

    os.mkdir(CURRENT_TEST_FOLDER)


    INPUT_VIDEO = os.path.join(CURRENT_TEST_FOLDER, 'input.avi')
    TRACKED_DATA = os.path.join(CURRENT_TEST_FOLDER, 'tracked_data.json')
    ANALYZED_DATA = os.path.join(CURRENT_TEST_FOLDER, 'analyzed_data.json')
    CROPPED_IMAGES_FOLDER = os.path.join(CURRENT_TEST_FOLDER, 'cropped_images')

    if not os.path.exists(CROPPED_IMAGES_FOLDER):
        os.mkdir(CROPPED_IMAGES_FOLDER)

    BACKGROUND = os.path.join(CURRENT_TEST_FOLDER, 'background.png')
    OUTPUT_VIDEO_NAME = video['name'][:video['name'].rfind('.')] + "_Synopsis.avi"
    OUTPUT_VIDEO = os.path.join(CURRENT_TEST_FOLDER, OUTPUT_VIDEO_NAME)



    myfile.save(INPUT_VIDEO)


    print('Tracking objects...')
    # tracker.track_video(INPUT_VIDEO, TRACKED_DATA, CROPPED_IMAGES_FOLDER)
    yolo_deepsort_detector.track_video(INPUT_VIDEO, TRACKED_DATA, CROPPED_IMAGES_FOLDER)

    print('Extracting the background...')
    background_extractor.extract(INPUT_VIDEO, BACKGROUND, CURRENT_TEST_FOLDER)

    print('Analyzing tracked data...')
    analyzer.analyze_json(TRACKED_DATA, ANALYZED_DATA)

    print('Making result video...')
    video_maker.make(CROPPED_IMAGES_FOLDER, ANALYZED_DATA, BACKGROUND, OUTPUT_VIDEO)
    myfile.save(OUTPUT_VIDEO)
    print('Result video saved to {}'.format(OUTPUT_VIDEO))

    # Move and delete redundant files and folders
    for file in os.listdir(CROPPED_IMAGES_FOLDER):
        os.remove(os.path.join(CROPPED_IMAGES_FOLDER, file))

    os.rmdir(CROPPED_IMAGES_FOLDER)
    os.remove(BACKGROUND)
    os.remove(TRACKED_DATA)
    os.remove(ANALYZED_DATA)

    print('Done')

    video['directory'] = CURRENT_TEST_FOLDER
    video['filename'] = OUTPUT_VIDEO_NAME

    if 'videos' not in session:
        session['videos'] = []
    session['videos'].append(video)
    session['current_video'] = video

    


    return redirect(url_for('download'))


@app.route('/download')
def download():
    return render_template('download.html')


if __name__ == '__main__':
    app.run()