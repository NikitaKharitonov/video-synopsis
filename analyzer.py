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

