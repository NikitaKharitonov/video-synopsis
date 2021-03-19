import json

def analyze_json(input_file_path, output_file_path):
    analyzed_data = {}
    with open(input_file_path, 'r') as input_file:
        tracked_data = json.load(input_file)
        activities = tracked_data['activities']
        for activity in activities.values():
            activity['start_frame'] = 0
        with open(output_file_path, 'w') as output_file:
            json.dump(tracked_data, output_file, indent=4)

def analyze_json2(input_file_path, output_file_path):
    analyzed_data = {}
    start_frame = 0
    with open(input_file_path, 'r') as input_file:
        tracked_data = json.load(input_file)
        activities = tracked_data['activities']
        for activity in activities.values():
            activity['start_frame'] = start_frame
            start_frame += 10
        with open(output_file_path, 'w') as output_file:
            json.dump(tracked_data, output_file, indent=4)

def get_activity_area_all_frames(input_file_path):
    analyzed_data = {}
    start_frame = 0
    with open(input_file_path, 'r') as input_file:
        tracked_data = json.load(input_file)
        activities = tracked_data['activities']
        print(get_overlap_area(activities['16'], activities['5']))
        # for activity in activities.values():
        #     # print(activity['frame_count'], len(activity['bounding_boxes']))
        #     area = sum([(bbox['y_down'] - bbox['y_up']) * (bbox['x_right'] - bbox['x_left']) for bbox in activity['bounding_boxes']])
        #     print(area)

def get_overlap_area(a1, a2):
    start_frame_idx = max(a1['start_frame'], a2['start_frame'])
    end_frame_idx = min(a1['start_frame'] + a1['frame_count'] - 1, a2['start_frame'] + a2['frame_count'] - 1)
    a1_start = start_frame_idx - a1['start_frame']
    a2_start = start_frame_idx - a2['start_frame']
    area = 0
    for i in range(0, end_frame_idx - start_frame_idx):
        a1_bbox = a1['bounding_boxes'][a1_start+i]
        a2_bbox = a2['bounding_boxes'][a2_start+i]
        dx = min(a1_bbox['x_right'], a2_bbox['x_right']) - max(a1_bbox['x_left'], a2_bbox['x_left'])
        dy = min(a1_bbox['y_down'], a2_bbox['y_down']) - max(a1_bbox['y_up'], a2_bbox['y_up'])
        if (dx>=0) and (dy>=0):
            area += dx*dy
    return area

def get_tubes_from_activities(activities):
    tubes = []
    for a in activities.values():
        tube = []
        start_frame = a['start_frame']
        for idx, bbox in enumerate(a['bounding_boxes']):
            x = bbox['x_right'] - bbox['x_left']
            y = bbox['y_down'] - bbox['y_up']
            t = start_frame + idx
            tube.append((x, y, t))
        tubes.append(tube) 
    return tubes

def analyze_json3(input_file_path, output_file_path):
    analyzed_data = {}
    start_frame = 0
    with open(input_file_path, 'r') as input_file:
        tracked_data = json.load(input_file)
        activities = tracked_data['activities']
        for i1, (k1, a1) in enumerate(list(activities.items())[:-1]):
            for i2, (k2, a2) in enumerate(list(activities.items())[i1+1:]):
                while similarity(a1, a2) > 0.1:
                    a2['start_frame'] += 1
        with open(output_file_path, 'w') as out:
            json.dump(tracked_data, out, indent=4)

def similarity(a1, a2):
    a1_area = sum([(bbox['y_down'] - bbox['y_up']) * (bbox['x_right'] - bbox['x_left']) for bbox in a1['bounding_boxes']])
    a2_area = sum([(bbox['y_down'] - bbox['y_up']) * (bbox['x_right'] - bbox['x_left']) for bbox in a2['bounding_boxes']])
    overlap_area = get_overlap_area(a1, a2)
    union_area = a1_area + a2_area - overlap_area
    return overlap_area / union_area
