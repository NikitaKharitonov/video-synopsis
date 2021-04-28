import tracker
import analyzer
import video_maker
import shutil
import os
from datetime import datetime
import background_extractor
import yolo_deepsort_detector

CROPPED_IMAGES_FOLDER_NAME = 'cropped_images'
TRACKED_DATA_FILE_NAME = 'tracked_data.json'
ANALYZED_DATA_FILE_NAME = 'analyzed_data.json'
BACKGROUND_FILE_NAME = 'background.png'
TESTS_DIR_NAME = 'tests'
TIMESTAMP_FORMAT = "%Y_%m_%d_%H_%M_%S"

classes_list = ['person', 'car', 'bike']

def summarize(input_video_file_path, class_list_to_display, activity_collision_cost, cluster_collision_cost):

    if not os.path.exists(TESTS_DIR_NAME):
        os.mkdir(TESTS_DIR_NAME)

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    test_dir_name = os.path.join(TESTS_DIR_NAME, timestamp)

    while os.path.exists(test_dir_name):
        test_dir_name += '+'

    os.mkdir(test_dir_name)

    input_video_file_name = os.path.split(input_video_file_path)[-1]

    new_input_video_file_path = os.path.join(test_dir_name, input_video_file_name)
    tracked_data_file_path = os.path.join(test_dir_name, TRACKED_DATA_FILE_NAME)
    analyzed_data_file_path = os.path.join(test_dir_name, ANALYZED_DATA_FILE_NAME)
    cropped_images_dir_path = os.path.join(test_dir_name, CROPPED_IMAGES_FOLDER_NAME)

    if not os.path.exists(cropped_images_dir_path):
        os.mkdir(cropped_images_dir_path)

    background_file_path = os.path.join(test_dir_name, BACKGROUND_FILE_NAME)
    output_video_file_name = input_video_file_name[:input_video_file_name.rfind('.')] + "_Synopsis.avi"
    output_video_file_path = os.path.join(test_dir_name, output_video_file_name)

    shutil.copy(input_video_file_path, new_input_video_file_path)

    print('Tracking objects...')
    yolo_deepsort_detector.track_video(new_input_video_file_path, tracked_data_file_path, cropped_images_dir_path, classes_list)

    print('Extracting the background...')
    background_extractor.extract(new_input_video_file_path, background_file_path, test_dir_name)

    print('Analyzing tracked data...')
    analyzer.analyze_json(tracked_data_file_path, analyzed_data_file_path, class_list_to_display, activity_collision_cost, cluster_collision_costy)

    print('Making result video...')
    video_maker.make(cropped_images_dir_path, analyzed_data_file_path, background_file_path, output_video_file_path)
    # video.save(output_video_file_path)
    print('Output video saved to {}'.format(output_video_file_path))

    for filename in os.listdir(cropped_images_dir_path):
        file_path = os.path.join(cropped_images_dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    if os.path.exists(cropped_images_dir_path):
        os.rmdir(cropped_images_dir_path)
    if os.path.exists(background_file_path):
        os.remove(background_file_path)
    if os.path.exists(tracked_data_file_path):
        os.remove(tracked_data_file_path)
    if os.path.exists(analyzed_data_file_path):
        os.remove(analyzed_data_file_path)

    print('Done')

    return output_video_file_path
