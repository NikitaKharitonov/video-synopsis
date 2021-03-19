import json
import cv2
import numpy as np
import os

def make(cropped_images_dir, data_filename, background_filename, output_video_path):
    background = cv2.imread(background_filename)

    with open(data_filename, 'r') as file:
        data = json.load(file)
        activities = data['activities']
        frame_total_number = max([int(x['start_frame']) + int(x['frame_count']) for x in activities.values()])
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'XVID'), 40,
                            (background.shape[1], background.shape[0]))

        alpha = 0.5

        for frame_idx in range(0, frame_total_number):
            img = np.copy(background)

            for id, activity in activities.items():
                if activity['start_frame'] <= frame_idx < activity['start_frame'] + activity['frame_count']:
                    cropped_img = cv2.imread(os.path.join(cropped_images_dir, id, '{}.png'.format(frame_idx - activity['start_frame'])))
                    if cropped_img is not None:
                        bbox = activity['bounding_boxes'][frame_idx - activity['start_frame']]
                        y0, x0, y1, x1 = bbox['y_up'], bbox['x_left'], bbox['y_down'], bbox['x_right']
                        x, y, w, h = x0, y0, x1 - x0, y1 - y0
                        place = img[y:y + h, x:x + w]
                        try:
                            added_image = cv2.addWeighted(place, alpha, cropped_img, 1 - alpha, 0)
                            img[y:y + h, x:x + w] = added_image
                            img = cv2.putText(img, 'time', (x0, y1), cv2.FONT_HERSHEY_SIMPLEX, cropped_img.shape[1] / 140,
                                            (0, 255, 0), 1)

                        except Exception:
                            print('ERROR!')
                            print(place.shape)
                            print(cropped_img.shape)
                            print(frame_idx, id)
            out.write(img)

        out.release()
