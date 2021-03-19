import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

# import ntpath
# import random
# from datetime import datetime
import yolo_deepsort_detector
import analyzer
import background_extractor
import video_maker
# import shutil

if __name__ == '__main__':
    test_dir_path = 'tests2'

    for case_dir_name in os.listdir(test_dir_path):
        case_dir_path = os.path.join(test_dir_path, case_dir_name)
        input_video_file_path = os.path.join(case_dir_path, 'input.avi')
        output_video_file_path = os.path.join(case_dir_path, 'output.avi')
        tracked_data = os.path.join(case_dir_path, 'tracked_data.json')
        cropped_images = os.path.join(case_dir_path, 'cropped_images')
        bg = os.path.join(case_dir_path, 'bg.png')
        analyzed_data = os.path.join(case_dir_path, 'analyzed_data.json')

        # yolo_deepsort_detector.track_video(input_video_file_path, tracked_data, cropped_images)
        # background_extractor.extract(input_video_file_path, bg, case_dir_path)
        analyzer.analyze_json3(tracked_data, analyzed_data)
        video_maker.make(cropped_images, analyzed_data, bg, output_video_file_path)
