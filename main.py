import tracker
import analyzer
import video_maker
import shutil
import os
from datetime import datetime
import background_extractor


# Initialize required paths
INPUT_VIDEO = 'input.avi'
TRACKED_DATA = 'tracked_data.json'
ANALYZED_DATA = 'analyzed_data.json'
CROPPED_IMAGES_FOLDER = 'cropped_images'

if not os.path.exists(CROPPED_IMAGES_FOLDER):
    os.mkdir(CROPPED_IMAGES_FOLDER)

BACKGROUND = 'background.png'
OUTPUT_VIDEO_FILENAME = 'output.avi'
TESTS_FOLDER = 'tests'
TIMESTAMP_FORMAT = "%Y_%m_%d_%H_%M_%S"

if not os.path.exists(TESTS_FOLDER):
    os.mkdir(TESTS_FOLDER)

timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
CURRENT_TEST_FOLDER = os.path.join(TESTS_FOLDER, timestamp)

if not os.path.exists(CURRENT_TEST_FOLDER):
    os.mkdir(CURRENT_TEST_FOLDER)

OUTPUT_VIDEO = os.path.join(CURRENT_TEST_FOLDER, OUTPUT_VIDEO_FILENAME)

print('Tracking objects...')
tracker.track_video(INPUT_VIDEO, TRACKED_DATA, CROPPED_IMAGES_FOLDER)

print('Extracting the background...')
background_extractor.extract(INPUT_VIDEO, BACKGROUND, CURRENT_TEST_FOLDER)

print('Analyzing tracked data...')
analyzer.analyze_json(TRACKED_DATA, ANALYZED_DATA)

print('Making result video...')
video_maker.make(CROPPED_IMAGES_FOLDER, ANALYZED_DATA, BACKGROUND, OUTPUT_VIDEO)
print(f'Result video saved to {OUTPUT_VIDEO}')

# Copy the original video to the sample folder
shutil.copy(INPUT_VIDEO, CURRENT_TEST_FOLDER)

# Move and delete redundant files and folders
for file in os.listdir(CROPPED_IMAGES_FOLDER):
    os.remove(os.path.join(CROPPED_IMAGES_FOLDER, file))

os.rmdir(CROPPED_IMAGES_FOLDER)
os.remove(BACKGROUND)
os.remove(TRACKED_DATA)
os.remove(ANALYZED_DATA)

print('Done')