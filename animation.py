import json
import cv2
import numpy as np
import os


test_dir_path = 'tests2'
images_dir_path = 'images'
background_path = os.path.join(images_dir_path, 'bg.png')
background = cv2.imread(background_path)
W, H = background.shape[1], background.shape[0]
person_path = os.path.join(images_dir_path, 'person.png')
person = cv2.imread(person_path)
h, w = person.shape[0], person.shape[1]


def draw(img, track, frame_idx):
    for idx, point in enumerate(track[:-1]):
        if point[2] <= frame_idx < track[idx + 1][2] or point[2] >= frame_idx > track[idx + 1][2]:
            x = (frame_idx - point[2]) * (track[idx + 1][0] - point[0]) / (track[idx + 1][2] - point[2]) + point[0]
            y = (frame_idx - point[2]) * (track[idx + 1][1] - point[1]) / (track[idx + 1][2] - point[2]) + point[1]
            x, y = int(x), int(y)
            img[y:y + h, x:x + w] = person


def case1():
    case_dir_path = os.path.join(test_dir_path, 'case1')
    if not os.path.exists(case_dir_path):
        os.mkdir(case_dir_path)
    video_path = os.path.join(case_dir_path, 'input.avi')
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 40, (W, H))

    for i in range(3):
        track = [(480, 0, 0), (200, H - h, 200)]
        for frame_idx in range(0, 200):
            img = np.copy(background)
            draw(img, track, frame_idx)
            out.write(img)

    out.release()

def case2():
    case_dir_path = os.path.join(test_dir_path, 'case2')
    if not os.path.exists(case_dir_path):
        os.mkdir(case_dir_path)
    video_path = os.path.join(case_dir_path, 'input.avi')
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 40, (W, H))

    track = [(480, 0, 0), (200, H - h, 200)]
    track2 = [(200, H - h, 0), (480, 0, 200)]

    for frame_idx in range(0, 200):
        img = np.copy(background)
        draw(img, track, frame_idx)
        draw(img, track2, frame_idx)
        out.write(img)

    out.release()

def case3():
    case_dir_path = os.path.join(test_dir_path, 'case3')
    if not os.path.exists(case_dir_path):
        os.mkdir(case_dir_path)
    video_path = os.path.join(case_dir_path, 'input.avi')
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 40, (W, H))


    for i in range(3):
        track = [(480, 0, 0), (200, H - h, 200)]
    
        for frame_idx in range(0, 200):
            img = np.copy(background)
            draw(img, track, frame_idx)
            out.write(img)

        track = [(380, 0, 0), (100, H - h, 200)]
        
        for frame_idx in range(0, 200):
            img = np.copy(background)
            draw(img, track, frame_idx)
            out.write(img)

    out.release()


if __name__ == '__main__':
    case1()
    case2()
    case3()