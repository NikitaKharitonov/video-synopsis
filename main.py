import summarizer
import os
import ntpath
import random
from datetime import datetime

if __name__ == '__main__':
    input_video_file_path = os.path.join('videos', 'pedestrian.avi')
    summarizer.summarize(input_video_file_path)