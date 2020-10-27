import tracker
import analyzer
import video_maker
import shutil
import os
from datetime import datetime

# Initialize required paths
ORIGINAL_VIDEO = 'original.avi'
TRACKED_DATA = 'tracked_data'
ANALYZED_DATA = 'analyzed_data.json'
CROPPED_IMAGES_FOLDER = 'cropped_images'

if not os.path.exists(CROPPED_IMAGES_FOLDER):
    os.mkdir(CROPPED_IMAGES_FOLDER)

BACKGROUND = 'background.png'
RESULT_VIDEO_FILENAME = 'result.avi'
RESULTS_FOLDER = 'results'
TIMESTAMP_FORMAT = "%Y_%m_%d_%H_%M_%S"

if not os.path.exists(RESULTS_FOLDER):
    os.mkdir(RESULTS_FOLDER)

timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
RESULT_FOLDER = os.path.join(RESULTS_FOLDER, timestamp)

if not os.path.exists(RESULT_FOLDER):
    os.mkdir(RESULT_FOLDER)

RESULT_VIDEO = os.path.join(RESULT_FOLDER, RESULT_VIDEO_FILENAME)

print('Tracking objects...')
tracker.track_camera(0, ORIGINAL_VIDEO, TRACKED_DATA, CROPPED_IMAGES_FOLDER, BACKGROUND)

print('Analyzing tracked data...')
analyzer.process(TRACKED_DATA, ANALYZED_DATA)

print('Making result video...')
video_maker.make(CROPPED_IMAGES_FOLDER, ANALYZED_DATA, BACKGROUND, RESULT_VIDEO)

# Copy the original video to the sample folder
shutil.copy(ORIGINAL_VIDEO, RESULT_FOLDER)

# Move and delete redundant files and folders
for file in os.listdir(CROPPED_IMAGES_FOLDER):
    os.remove(os.path.join(CROPPED_IMAGES_FOLDER, file))

os.rmdir(CROPPED_IMAGES_FOLDER)
os.remove(BACKGROUND)
os.remove(TRACKED_DATA)
os.remove(ANALYZED_DATA)

print('Done')
