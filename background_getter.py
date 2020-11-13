import numpy as np
import cv2 as cv
import os

FRAMES_FOLDER = 'frames'


def get(video_filename, background_path):
    if os.path.exists(FRAMES_FOLDER):
        for file in os.listdir(FRAMES_FOLDER):
            os.remove(os.path.join(FRAMES_FOLDER, file))
        os.rmdir(FRAMES_FOLDER)
    os.mkdir(FRAMES_FOLDER)

    cap = cv.VideoCapture(video_filename)

    cnt = 0
    while True:
        ret, frame = cap.read()
        if ret is False:
            break
        cv.imwrite(os.path.join(FRAMES_FOLDER, f'{cnt}.png'), frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        cnt += 1

    cap.release()
    cv.destroyAllWindows()

    background = cv.imread(os.path.join(FRAMES_FOLDER, '0.png'))
    background = background / 255.0
    cnt = 1
    while True:
        try:
            frame = cv.imread(os.path.join(FRAMES_FOLDER, f'{cnt}.png'))
            frame = frame / 255.0
            background = background + frame
            cnt += 1
        except Exception:
            break
    background /= cnt
    background *= 255
    cv.imwrite(background_path, background)
    for file in os.listdir(FRAMES_FOLDER):
        os.remove(os.path.join(FRAMES_FOLDER, file))
    os.rmdir(FRAMES_FOLDER)
