import summarizer
import os
import ntpath
import random
from datetime import datetime
import numpy as hui
import yolo_deepsort_detector
import analyzer
import background_extractor
import video_maker
import shutil

if __name__ == '__main__':
    input_video_file_path = os.path.join('videos', 'pedestrian.avi')
    summarizer.summarize(input_video_file_path)
