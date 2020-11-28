#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

# from timeit import time
import warnings
import cv2
import os
import datetime
import numpy as np
from PIL import Image
import json
from yolo import YOLO

from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.detection_yolo import Detection_YOLO
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet
from tracker import draw_box_label, crop

# import imutils.video

warnings.filterwarnings('ignore')


def track_video(file_path, tracked_data_output_file, cropped_images_folder):
    yolo = YOLO()
    fps = 0
    if not os.path.exists(cropped_images_folder):
        os.mkdir(cropped_images_folder)

    # Definition of the parameters
    max_cosine_distance = 0.3
    nn_budget = None
    nms_max_overlap = 1.0

    # Deep SORT
    model_filename = 'models/yolov4/mars-small128.pb'
    encoder = gdet.create_box_encoder(model_filename, batch_size=1)

    metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
    tracker = Tracker(metric)

    tracking = True
    writeVideo_flag = True

    video_capture = cv2.VideoCapture(file_path)

    tracked_data = {'frames': []}

    # if writeVideo_flag:
    #     w = int(video_capture.get(3))
    #     h = int(video_capture.get(4))
    #     fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #     out = cv2.VideoWriter('output_yolov4.avi', fourcc, 30, (w, h))
    #     frame_index = -1

    fps = 0.0
    # fps_imutils = imutils.video.FPS().start()

    # The list of frames counts for each tracked object
    frame_counts = {}
    frame_count = 0

    while True:

        fps = video_capture.get(cv2.CAP_PROP_FPS)

        ret, frame = video_capture.read()  # frame shape 640*480*3
        if ret != True:
            break

        # t1 = time.time()

        image = Image.fromarray(frame[..., ::-1])  # bgr to rgb
        boxes, confidence, classes = yolo.detect_image(image)

        if tracking:
            features = encoder(frame, boxes)

            detections = [Detection(bbox, confidence, cls, feature) for bbox, confidence, cls, feature in
                          zip(boxes, confidence, classes, features)]
        else:
            detections = [Detection_YOLO(bbox, confidence, cls) for bbox, confidence, cls in
                          zip(boxes, confidence, classes)]

        # Run non-maxima suppression.
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]

        if tracking:
            # Call the tracker
            tracker.predict()
            tracker.update(detections)

            # if len(tracker.tracks) > 0:
            #     max_trk_id = np.max([track.track_id for track in tracker.tracks])
            #     if len(frame_counts) - 1 < max_trk_id:
            #         np.concatenate((frame_counts, np.zeros(max_trk_id - len(frame_counts) + 1)))

            time = str(datetime.timedelta(seconds=frame_count / fps)).split('.')[0]

            # The list of tracks to be annotated
            frame_data = []
            for track in tracker.tracks:
                if track.track_id not in frame_counts.keys():
                    frame_counts[track.track_id] = 0
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue
                bbox = track.to_tlbr()
                bbox = bbox.astype("int")

                # original_img = np.copy(frame)
                # print(bbox)
                # frame = draw_box_label(track.track_id, frame, [bbox[1], bbox[0], bbox[3], bbox[2]], (255, 255, 255))  # Draw the bounding boxes on the images
                cropped_img = crop(frame, [bbox[1], bbox[0], bbox[3], bbox[2]])

                object_data = {'id': int(track.track_id), 'y_up': int(bbox[1]), 'x_left': int(bbox[0]), 'y_down': int(bbox[3]),
                               'x_right': int(bbox[2]), 'time': time}
                frame_data.append(object_data)

                if cropped_img.shape[0] != 0 and cropped_img.shape[1] != 0:
                    cv2.imwrite(
                        os.path.join(cropped_images_folder, '{}_{}.png'.format(frame_counts[track.track_id], track.track_id)),
                        cropped_img)
                frame_counts[track.track_id] += 1

                # frame_counts[track.track_id] += 1
            tracked_data['frames'].append(frame_data)


        # for det in detections:
        #     bbox = det.to_tlbr()
        # score = "%.2f" % round(det.confidence * 100, 2) + "%"
        # cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0), 2)
        # if len(classes) > 0:
        #     cls = det.cls
        # cv2.putText(frame, str(cls) + " " + score, (int(bbox[0]), int(bbox[3])), 0,
        #             1.5e-3 * frame.shape[0], (0, 255, 0), 1)

        # cv2.imshow('', frame)

        # if writeVideo_flag:  # and not asyncVideo_flag:
        #     # save a frame
        #     out.write(frame)
        #     frame_index = frame_index + 1

        # fps_imutils.update()

        # fps = (fps + (1./(time.time()-t1))) / 2
        # print("FPS = %f"%(fps))

        # Press Q to stop!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    # fps_imutils.stop()
    # print('imutils FPS: {}'.format(fps_imutils.fps()))
    # print(tracked_data)
    with open(tracked_data_output_file, "w") as file:
        json.dump(tracked_data, file, indent=4)

    video_capture.release()

    # if writeVideo_flag:
    #     out.release()

    cv2.destroyAllWindows()


