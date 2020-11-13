import json


# def analyze(input_file, output_file):
#     data = []
#     with open(input_file) as f:
#         while True:
#             line = f.readline()
#             if not line:
#                 break
#             str_list = line.replace('[', '').replace(']', '').replace('\n', '').split(', ')
#             if len(str_list) > 1:
#                 data.append(list(map(int, str_list)))
#
#     data_dict = {}
#     for arr in data:
#         if not str(arr[0]) in data_dict.keys():
#             data_dict[str(arr[0])] = []
#         data_dict[str(arr[0])].append([arr[1], arr[2], arr[3], arr[4]])
#
#     with open(output_file, 'w') as input_file:
#         json.dump(data_dict, input_file, indent=4)


def analyze_json(input_file_path, output_file_path):
    middle_data = {}
    analyzed_data = {'frames':[]}
    with open(input_file_path, 'r') as input_file:
        tracked_data = json.load(input_file)
        frames = tracked_data['frames']
        for frame in frames:
            for object_data in frame:
                if not str(object_data['id']) in middle_data.keys():
                    middle_data[str(object_data['id'])] = []
                middle_data[str(object_data['id'])].append(object_data)
        with open(output_file_path, 'w') as output_file:
            json.dump(middle_data, output_file, indent=4)
        # max_frame_count = max([len(x) for x in middle_data.values()])
        # new_frames = []
        # for frame_index in range(0, max_frame_count):
        #     for object_frames in middle_data:
        #         if frame_index < len(object_frames):
        #             new_frames.append()



