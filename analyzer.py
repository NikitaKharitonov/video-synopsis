import json


def process(input_file, output_file):
    data = []
    with open(input_file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            str_list = line.replace('[', '').replace(']', '').replace('\n', '').split(', ')
            if len(str_list) > 1:
                data.append(list(map(int, str_list)))

    data_dict = {}
    for arr in data:
        if not str(arr[0]) in data_dict.keys():
            data_dict[str(arr[0])] = []
        data_dict[str(arr[0])].append([arr[1], arr[2], arr[3], arr[4]])

    with open(output_file, 'w') as input_file:
        json.dump(data_dict, input_file, indent=4)
