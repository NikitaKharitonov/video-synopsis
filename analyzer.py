import json

# def analyze_json(input_file_path, output_file_path):
#     analyzed_data = {}
#     with open(input_file_path, 'r') as input_file:
#         tracked_data = json.load(input_file)
#         activities = tracked_data['activities']
#         for activity in activities.values():
#             activity['start_frame'] = 0
#         with open(output_file_path, 'w') as output_file:
#             json.dump(tracked_data, output_file, indent=4)

def get_similarity(a1, a2):
    start_frame_idx = max(a1['start_frame'], a2['start_frame'])
    end_frame_idx = min(a1['start_frame'] + a1['frame_count'] - 1, a2['start_frame'] + a2['frame_count'] - 1)
    a1_start = start_frame_idx - a1['start_frame']
    a2_start = start_frame_idx - a2['start_frame']
    similarity = 0
    for i in range(0, end_frame_idx - start_frame_idx):
        a1_bbox = a1['bounding_boxes'][a1_start+i]
        a2_bbox = a2['bounding_boxes'][a2_start+i]
        dx = min(a1_bbox['x_right'], a2_bbox['x_right']) - max(a1_bbox['x_left'], a2_bbox['x_left'])
        dy = min(a1_bbox['y_down'], a2_bbox['y_down']) - max(a1_bbox['y_up'], a2_bbox['y_up'])
        if (dx>=0) and (dy>=0):
            area = dx*dy
            a1_area = (a1_bbox['y_down'] - a1_bbox['y_up']) * (a1_bbox['x_right'] - a1_bbox['x_left'])
            a2_area = (a2_bbox['y_down'] - a2_bbox['y_up']) * (a2_bbox['x_right'] - a2_bbox['x_left'])
            # union_area = a1_area + a2_area - area
            similarity += area / min(a1_area, a2_area)
    if end_frame_idx - start_frame_idx + 1 == 0:
        return 0
    return similarity / (end_frame_idx - start_frame_idx + 1)

# def get_tubes_from_activities(activities):
#     tubes = []
#     for a in activities.values():
#         tube = []
#         start_frame = a['start_frame']
#         for idx, bbox in enumerate(a['bounding_boxes']):
#             x = bbox['x_right'] - bbox['x_left']
#             y = bbox['y_down'] - bbox['y_up']
#             t = start_frame + idx
#             tube.append((x, y, t))
#         tubes.append(tube) 
#     return tubes

def analyze_json(input_file_path, output_file_path):
    analyzed_data = {}
    start_frame = 0
    with open(input_file_path, 'r') as input_file:
        tracked_data = json.load(input_file)
        activities = tracked_data['activities']
        for activity in activities.values():
            activity['start_frame'] = 0
        clusters = get_clusters(activities)
        print(len(clusters))
        for cluster in clusters:
            print(len(cluster))
            for i1, (k1, a1) in enumerate(list(cluster.items())[:-1]):
                for i2, (k2, a2) in enumerate(list(cluster.items())[i1+1:]):
                    while get_similarity(a1, a2) > 0.1:
                        a2['start_frame'] += 1
        for idx1, cluster1 in enumerate(clusters[:-1]):
            for idx2, cluster2 in enumerate(clusters[idx1 + 1:]):
                overlap = 0
                for k1, a1 in cluster1.items():
                    for k2, a2 in cluster2.items():
                        overlap += get_similarity(a1, a2)
                print(idx1, idx2, 'overlap', overlap)
                while overlap > 0.5:
                    for k2, a2 in cluster2.items():
                        a2['start_frame'] += 1
                    overlap = 0
                    for k1, a1 in cluster1.items():
                        for k2, a2 in cluster2.items():
                            overlap += get_similarity(a1, a2)
        for cluster in clusters:
            activities.update(cluster)
        tracked_data['activities'] = activities
        with open(output_file_path, 'w') as out:
            json.dump(tracked_data, out, indent=4)

def get_clusters(activities):
    clusters = []
    activities = list(activities.items())
    for idx1, val1 in enumerate(activities):
        if val1 is not None:
            k1, a1 = val1
            cluster = {k1: a1}
            activities[idx1] = None
            for idx2, val2 in enumerate(activities):
                if val2 is not None:
                    k2, a2 = val2
                    if get_overlap_area(a1, a2) > 0.1:
                        cluster.update({k2: a2})
                        activities[idx2] = None
            clusters.append(cluster)
    return clusters
            