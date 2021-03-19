# import summarizer
import os
# import ntpath
# import random
# from datetime import datetime
import yolo_deepsort_detector
import analyzer
# import background_extractor
import video_maker
# import shutil

if __name__ == '__main__':
    input_video_file_path = os.path.join('videos', 'pedestrian.avi')
    # summarizer.summarize(input_video_file_path)
    # yolo_deepsort_detector.track_video('generated_input_video.avi', 'tracked_data2.json', 'cropped_images2')
    # background_extractor.extract(input_video_file_path, 'bg.png', 'test')
    # analyzer.analyze_json2('tracked_data.json', 'analyzed_data.json')
    video_maker.make('cropped_images2', 'analyzed_analyzed_data.json', 'bg.png', 'output3.avi')
    # analyzer.get_activity_area_all_frames('tracked_data.json')
    # analyzer.analyze_json('tracked_data2.json', 'analyzed_data2.json')
    # analyzer.analyze_json3('analyzed_data2.json')
