import os
import cv2
import numpy as np

weights_path = "models/yolo/yolov3.weights"
config_path = "models/yolo/yolov3.cfg"

net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# initialize the video stream, pointer to output video file, and
# frame dimensions
vs = cv2.VideoCapture("input.avi")
print('helo')
# loop over frames from the video file stream
while True:
    # read the next frame from the file
    (grabbed, frame) = vs.read()
    # if the frame was not grabbed, then we have reached the end
    # of the stream
    if not grabbed:
        break

    (H, W) = frame.shape[:2]
    # construct a blob from the input frame and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes
    # and associated probabilities
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)
    # initialize our lists of detected bounding boxes, confidences,
    # and class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability)
            # of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > 0.5:
                # scale the bounding box coordinates back relative to
                # the size of the image, keeping in mind that YOLO
                # actually returns the center (x, y)-coordinates of
                # the bounding box followed by the boxes' width and
                # height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                # use the center (x, y)-coordinates to derive the top
                # and and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # update our list of bounding box coordinates,
                # confidences, and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)
        # apply non-maxima suppression to suppress weak, overlapping
        # bounding boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.5)
        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                # draw a bounding box rectangle and label on the frame
                color = (255, 0, 0)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format("person",
                                           confidences[i])
                cv2.putText(frame, text, (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the file pointers
print("[INFO] cleaning up...")
vs.release()

# image = cv2.imread("lenna.png")
# (h, w) = image.shape[:2]
#
# ln = net.getLayerNames()
# ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
#
# blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
# net.setInput(blob)
# layerOutputs = net.forward(ln)
#
# boxes = []
# confidences = []
# classIDs = []
#
# for output in layerOutputs:
#     # loop over each of the detections
#     for detection in output:
#         # extract the class ID and confidence (i.e., probability) of
#         # the current object detection
#         scores = detection[5:]
#         classID = np.argmax(scores)
#         confidence = scores[classID]
#         # filter out weak predictions by ensuring the detected
#         # probability is greater than the minimum probability
#         if confidence > 0.5:
#             # scale the bounding box coordinates back relative to the
#             # size of the image, keeping in mind that YOLO actually
#             # returns the center (x, y)-coordinates of the bounding
#             # box followed by the boxes' width and height
#             box = detection[0:4] * np.array([w, h, w, h])
#             (centerX, centerY, width, height) = box.astype("int")
#             # use the center (x, y)-coordinates to derive the top and
#             # and left corner of the bounding box
#             x = int(centerX - (width / 2))
#             y = int(centerY - (height / 2))
#             # update our list of bounding box coordinates, confidences,
#             # and class IDs
#             boxes.append([x, y, int(width), int(height)])
#             confidences.append(float(confidence))
#             classIDs.append(classID)
#
# idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5,
#                         0.5)
#
# if len(idxs) > 0:
#     # loop over the indexes we are keeping
#     for i in idxs.flatten():
#         # extract the bounding box coordinates
#         (x, y) = (boxes[i][0], boxes[i][1])
#         (w, h) = (boxes[i][2], boxes[i][3])
#         # draw a bounding box rectangle and label on the image
#         color = (255, 0, 0)
#         cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
#         text = "{}: {:.4f}".format("person", confidences[i])
#         cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5, color, 2)
# # show the output image
# cv2.imshow("Image", image)
# cv2.waitKey(0)
