import numpy as np
from scipy.optimize import linear_sum_assignment
import cv2
import random
from numpy import dot
from scipy.linalg import block_diag
from scipy.linalg import inv
import os
import json

# Global variables to be used by functions of VideoFileClop
frame_count = 0  # frame counter
tracker_count = 0
max_age = 15  # no.of consecutive unmatched detection before
# a track is deleted
min_hits = 1  # no. of consecutive matches needed to establish a track
tracker_list = []  # list for trackers
MODEL_TYPES = ['ssd_mobilenet_v1_coco_2017_11_17/', 'ssd_mobilenet_v3_large_coco_2020_01_14/']
models_path = 'models/'
model_type = MODEL_TYPES[1]
config_file_name = 'config.pbtxt'
weights_file_name = '/weights.pb'
config_path = 'models/' + model_type + config_file_name
weights_path = 'models/' + model_type + weights_file_name
net = cv2.dnn_DetectionModel(weights_path, config_path)
net.setInputSize((320, 320))
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)
conf_threshold = 0.6


def box_iou2(a, b):
    """
    Helper function to calculate the ratio between intersection and the union of
    two boxes a and b
    a[0], a[1], a[2], a[3] <-> left, up, right, bottom
    """

    w_intsec = np.maximum(0, (np.minimum(a[2], b[2]) - np.maximum(a[0], b[0])))
    h_intsec = np.maximum(0, (np.minimum(a[3], b[3]) - np.maximum(a[1], b[1])))
    s_intsec = w_intsec * h_intsec
    s_a = (a[2] - a[0]) * (a[3] - a[1])
    s_b = (b[2] - b[0]) * (b[3] - b[1])

    return float(s_intsec) / (s_a + s_b - s_intsec)


def draw_box_label(id, img, bbox_cv2, box_color=(0, 255, 255), show_label=True):
    """
    Helper function for drawing the bounding boxes and the labels
    bbox_cv2 = [left, top, right, bottom]
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.3
    font_color = (0, 0, 0)
    left, top, right, bottom = bbox_cv2[1], bbox_cv2[0], bbox_cv2[3], bbox_cv2[2]

    # Draw the bounding box
    # cv2.rectangle(img, (left, top), (right, bottom), box_color, 4)
    cv2.rectangle(img, (left, top), (right, bottom), box_color, 1)

    if show_label:
        # Draw a filled box on top of the bounding box (as the background for the labels)
        # cv2.rectangle(img, (left-2, top-45), (right+2, top), box_color, -1, 1)
        cv2.rectangle(img, (left, top - 10), (right, top), box_color, -1, 1)

        # Output the labels that show the x and y coordinates of the bounding box center.
        # text_x= 'id='+str(id)
        # cv2.putText(img,text_x,(left,top-25), font, font_size, font_color, 1, cv2.LINE_AA)
        # text_y= 'y='+str((top+bottom)/2)
        # cv2.putText(img,text_y,(left,top-5), font, font_size, font_color, 1, cv2.LINE_AA)
        text_x = str(id)
        cv2.putText(img, text_x, (left, top - 2), font, font_size, font_color, 1, cv2.LINE_AA)

    return img


def detect_humans(frame):
    class_ids, _, bboxes = net.detect(frame, confThreshold=conf_threshold)
    # human_bboxes = [x for bbox in collected_data if ]
    if len(class_ids) != 0:
        class_ids = class_ids.flatten()
        human_bboxes = []
        for index, value in enumerate(bboxes):
            if class_ids[index] == 1:
                human_bboxes.append(value)
        return human_bboxes
    else:
        return []


class Tracker:  # class for Kalman Filter based tracker
    def __init__(self):
        self.frame = 0
        # Initialize parameters for tracker (history)
        self.id = 0  # tracker's id
        self.color = (0, 0, 0)  # tracker's color
        self.box = []  # list to store the coordinates for a bounding box
        self.hits = 0  # number of detection matches
        self.no_losses = 0  # number of unmatched tracks (track loss)

        # Initialize parameters for Kalman Filtering
        # The state is the (x, y) coordinates of the detection box
        # state: [up, up_dot, left, left_dot, down, down_dot, right, right_dot]
        # or[up, up_dot, left, left_dot, height, height_dot, width, width_dot]
        self.x_state = []
        self.dt = 1.  # time interval

        # Process matrix, assuming constant velocity model
        self.F = np.array([[1, self.dt, 0, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 0, 1, self.dt, 0, 0, 0, 0],
                           [0, 0, 0, 1, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, self.dt, 0, 0],
                           [0, 0, 0, 0, 0, 1, 0, 0],
                           [0, 0, 0, 0, 0, 0, 1, self.dt],
                           [0, 0, 0, 0, 0, 0, 0, 1]])

        # Measurement matrix, assuming we can only measure the coordinates

        self.H = np.array([[1, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 1, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 1, 0]])

        # Initialize the state covariance
        self.L = 100.0
        self.P = np.diag(self.L * np.ones(8))

        # Initialize the process covariance
        self.Q_comp_mat = np.array([[self.dt ** 4 / 2., self.dt ** 3 / 2.],
                                    [self.dt ** 3 / 2., self.dt ** 2]])
        self.Q = block_diag(self.Q_comp_mat, self.Q_comp_mat,
                            self.Q_comp_mat, self.Q_comp_mat)

        # Initialize the measurement covariance
        self.R_ratio = 1.0 / 16.0
        self.R_diag_array = self.R_ratio * np.array([self.L, self.L, self.L, self.L])
        self.R = np.diag(self.R_diag_array)

    def kalman_filter(self, z):
        """
        Implement the Kalman Filter, including the predict and the update stages,
        with the measurement z
        """
        x = self.x_state
        # Predict
        x = dot(self.F, x)
        self.P = dot(self.F, self.P).dot(self.F.T) + self.Q

        # Update
        S = dot(self.H, self.P).dot(self.H.T) + self.R
        K = dot(self.P, self.H.T).dot(inv(S))  # Kalman gain
        y = z - dot(self.H, x)  # residual
        x += dot(K, y)
        self.P = self.P - dot(K, self.H).dot(self.P)
        self.x_state = x.astype(int)  # convert to integer coordinates
        # (pixel values)

    def predict_only(self):
        """
        Implement only the predict stage. This is used for unmatched detections and
        unmatched tracks
        """
        x = self.x_state
        # Predict
        x = dot(self.F, x)
        self.P = dot(self.F, self.P).dot(self.F.T) + self.Q
        self.x_state = x.astype(int)


def assign_detections_to_trackers(trackers, detections, iou_thrd=0.01):
    """
    From current list of trackers and new detections, output matched detections,
    unmatched trackers, unmatched detections.
    """

    IOU_mat = np.zeros((len(trackers), len(detections)), dtype=np.float32)
    for t, trk in enumerate(trackers):
        for d, det in enumerate(detections):
            # IOU_mat[t, d] = helpers.box_iou2(trk, det)
            IOU_mat[t, d] = box_iou2(trk, det)

    # Produces matches
    # Solve the maximizing the sum of IOU assignment problem using the
    # Hungarian algorithm (also known as Munkres algorithm)

    matched_idx = linear_sum_assignment(-IOU_mat)
    matched_idx = np.asarray(matched_idx)
    matched_idx = np.transpose(matched_idx)

    unmatched_trackers, unmatched_detections = [], []
    for t, trk in enumerate(trackers):
        if t not in matched_idx[:, 0]:
            unmatched_trackers.append(t)

    for d, det in enumerate(detections):
        if d not in matched_idx[:, 1]:
            unmatched_detections.append(d)

    matches = []

    # For creating trackers we consider any detection with an
    # overlap less than iou_thrd to signifiy the existence of
    # an untracked object

    for m in matched_idx:
        if IOU_mat[m[0], m[1]] < iou_thrd:
            unmatched_trackers.append(m[0])
            unmatched_detections.append(m[1])
        else:
            matches.append(m.reshape(1, 2))

    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


def crop(frame, bbox):
    y0, x0, y1, x1 = bbox[0], bbox[1], bbox[2], bbox[3]
    if y0 < 0 or y1 < 0 or x1 < 0 or x0 < 0:
        return []
    return frame[y0:y1, x0:x1]


def pipeline(original_img, cropped_images_path, tracked_data):
    """
    Pipeline function for detection and tracking
    """
    global frame_count
    global tracker_count
    global tracker_list
    global max_age
    global min_hits
    global track_id_list

    img = np.copy(original_img)

    detections = detect_humans(img)  # x y w h
    for index, det in enumerate(detections):
        detections[index] = [det[1], det[0], det[1] + det[3], det[0] + det[2]] # y_up x_left y_down x_right

    trackers = []

    if len(tracker_list) > 0:
        for trk in tracker_list:
            trackers.append(trk.box)

    matched, unmatched_dets, unmatched_trks = assign_detections_to_trackers(trackers, detections)

    # Deal with matched detections
    if matched.size > 0:
        for trk_idx, det_idx in matched:
            z = detections[det_idx]
            z = np.expand_dims(z, axis=0).T
            tmp_trk = tracker_list[trk_idx]
            tmp_trk.kalman_filter(z)
            xx = tmp_trk.x_state.T[0].tolist()
            xx = [xx[0], xx[2], xx[4], xx[6]]
            trackers[trk_idx] = xx
            tmp_trk.box = xx
            tmp_trk.hits += 1

    # Deal with unmatched detections
    if len(unmatched_dets) > 0:
        for idx in unmatched_dets:
            z = detections[idx]
            z = np.expand_dims(z, axis=0).T
            tmp_trk = Tracker()  # Create a new tracker
            x = np.array([[z[0], 0, z[1], 0, z[2], 0, z[3], 0]], dtype=object).T
            tmp_trk.x_state = x
            tmp_trk.predict_only()
            xx = tmp_trk.x_state
            xx = xx.T[0].tolist()
            # xx = xx[0].tolist()
            xx = [xx[0], xx[2], xx[4], xx[6]]
            tmp_trk.box = xx
            # assign an ID for the tracker
            tmp_trk.id = tracker_count
            tracker_count += 1
            tmp_trk.color = (random.randint(127, 255), random.randint(127, 255), random.randint(127, 255))
            tracker_list.append(tmp_trk)
            trackers.append(xx)

    # Deal with unmatched tracks
    if len(unmatched_trks) > 0:
        for trk_idx in unmatched_trks:
            tmp_trk = tracker_list[trk_idx]
            tmp_trk.no_losses += 1
            tmp_trk.predict_only()
            xx = tmp_trk.x_state
            xx = xx.T[0].tolist()
            xx = [xx[0], xx[2], xx[4], xx[6]]
            tmp_trk.box = xx
            trackers[trk_idx] = xx

    # The list of tracks to be annotated
    frame_data = []
    for trk in tracker_list:
        if (trk.hits >= min_hits) and (trk.no_losses <= max_age):
            x_cv2 = trk.box
            if x_cv2[0] > -1 and x_cv2[1] > -1 and x_cv2[2] > -1 and x_cv2[3] > -1:
                img = draw_box_label(trk.id, img, x_cv2, trk.color)  # Draw the bounding boxes on the images
                cropped_img = crop(original_img, trk.box)
                object_data = {'id':trk.id, 'y_up':x_cv2[0], 'x_left':x_cv2[1], 'y_down':x_cv2[2], 'x_right':x_cv2[3]}
                frame_data.append(object_data)
                # frame_data.append([trk.id, [x_cv2[0], x_cv2[1], x_cv2[2], x_cv2[3]]])
                if cropped_img.shape[0] != 0 and cropped_img.shape[1] != 0:
                    cv2.imwrite(os.path.join(cropped_images_path, f'{trk.frame}_{trk.id}.png'), cropped_img)
                trk.frame += 1

    tracked_data['frames'].append(frame_data)
    # file.write(str(frame_data) + '\n')

    tracker_list = [x for x in tracker_list if x.no_losses <= max_age]
    frame_count += 1

    return img


def track_video(input_video, tracked_data_output_file, cropped_images_folder):
    if not os.path.exists(cropped_images_folder):
        os.mkdir(cropped_images_folder)

    cap = cv2.VideoCapture(input_video)

    tracked_data = {'frames': []}

    while True:

        ret, img = cap.read()
        if not ret:
            break
        np.asarray(img)
        pipeline(img, cropped_images_folder, tracked_data)

    with open(tracked_data_output_file, "w") as file:
        json.dump(tracked_data, file)

    cap.release()
    cv2.destroyAllWindows()


def track_camera(number, input_video, tracked_data_output_file, cropped_images_folder):
    if not os.path.exists(cropped_images_folder):
        os.mkdir(cropped_images_folder)

    cap = cv2.VideoCapture(number)
    ret, frame = cap.read()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(input_video, fourcc, 40, (frame.shape[1], frame.shape[0]))

    tracked_data = {'frames': []}

    while True:

        ret, img = cap.read()
        if not ret:
            break
        np.asarray(img)
        new_img = pipeline(img, cropped_images_folder, tracked_data)
        cv2.imshow("frame", new_img)
        out.write(new_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    with open(tracked_data_output_file, "w") as file:
        json.dump(tracked_data, file)

    out.release()
    cap.release()
    cv2.destroyAllWindows()
