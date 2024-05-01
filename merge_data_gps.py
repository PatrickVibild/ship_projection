import os
import json
import random

def list_folders(path):
    return [f.name for f in os.scandir(path) if f.is_dir()]

path = '/home/patrick/Data/Incheon/dataset'
gps_folder= '/home/patrick/Data/Incheon/data'
folders = list_folders(path)
for folder in folders:
    meta_path = path + '/' + folder + '/meta.json'
    gps_path = gps_folder + '/' + folder + '/meta.json'

    try:
        with open(meta_path, 'r') as json_file:
            meta = json.load(json_file)
    except:
        print('error json ' + meta_path)
        continue

    try:
        with open(gps_path, 'r') as json_file:
            gps = json.load(json_file)
    except:
        print('missing field' + str(gps_path))
        continue

    frames = len(meta['euler'])
    gps_data = len(gps)
    gps_gaps = frames- gps_data
    for idx in range(gps_gaps):
        random_integer = random.randint(1, gps_data - 1)
        gps.insert(random_integer, gps[random_integer - 1])
    meta['gps'] = []
    gps_data_2 = len(gps)
    for idx in range(frames):
        meta['gps'].append(
            {
                'lat': gps[idx][0],
                'lon': gps[idx][1],
                'alt': gps[idx][2]
            }
        )

    with open(meta_path, 'w') as file:
        json.dump(meta, file, indent=4)
