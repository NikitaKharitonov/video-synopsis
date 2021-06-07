from __future__ import division, print_function, absolute_import

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


warnings.filterwarnings('ignore')


def track_video(file_path, tracked_data_output_file, cropped_images_folder, classes_list):
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

    tracked_data = {'activities': {}}

    fps = 0.0

    # The list of frames counts for each tracked object
    frame_count = 0
    frame_counts = {}

    if writeVideo_flag:
        out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (640,360))

    while True:

        fps = video_capture.get(cv2.CAP_PROP_FPS)

        ret, frame = video_capture.read()  
        if ret != True:
            break

        image = Image.fromarray(frame[..., ::-1])  # bgr to rgb
        boxes, confidence, classes = yolo.detect_image(image, classes_list)

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

            time = str(datetime.timedelta(seconds=frame_count / fps)).split('.')[0]

            # The list of tracks to be annotated
            activities = []
            for idx, track in enumerate(tracker.tracks):
                if track.track_id not in frame_counts.keys():
                    frame_counts[track.track_id] = 0
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue
                bbox = track.to_tlbr()
                bbox = bbox.astype("int")
                class_name = track.class_name

                cropped_img = crop(frame, [bbox[1], bbox[0], bbox[3], bbox[2]])

                activity_id = str(track.track_id)

                if writeVideo_flag:
                    # draw
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0), 6)
                    cv2.putText(frame, activity_id, (int(bbox[0]), int(bbox[1]) - 6), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)

                if activity_id not in tracked_data['activities'].keys():
                    tracked_data['activities'][activity_id] = {'class': class_name, 'start_frame': frame_count, 'frame_count': 0, 'bounding_boxes': []}
                tracked_data['activities'][activity_id]['bounding_boxes'].append({'y_up': int(bbox[1]), 'x_left': int(bbox[0]), 'y_down': int(bbox[3]), 'x_right': int(bbox[2]), 'time': time})
                tracked_data['activities'][activity_id]['frame_count'] += 1

                if cropped_img.shape[0] != 0 and cropped_img.shape[1] != 0:
                    activity_dir_path = os.path.join(cropped_images_folder, activity_id)
                    if not os.path.exists(activity_dir_path):
                        os.mkdir(activity_dir_path) 
                    cv2.imwrite(
                        os.path.join(activity_dir_path, '{}.png'.format(frame_counts[track.track_id])),
                        cropped_img)
                frame_counts[track.track_id] += 1

        if writeVideo_flag:
            # write
            out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    with open(tracked_data_output_file, "w") as file:
        json.dump(tracked_data, file, indent=4)

    out.release()
    video_capture.release()

    cv2.destroyAllWindows()
