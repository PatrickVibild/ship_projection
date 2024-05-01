import json
import cv2 as cv
from projector import load_camera_m, projection_baby
import os


def find_limits(lst, num):
    for i, val in enumerate(lst):
        if val > num:
            # Check if it's the first element of the list
            if i == 0:
                return (None, val)
            return (lst[i - 1], val)
    # If no larger number is found in the list, return the last number and None
    return (lst[-1], None)


def parse_json(path):
    f = open(path + '/meta.json')
    data = json.load(f)
    return data['gps'], data['euler'], data['ais']


def list_images_in_folder(folder_path):
    # Define a list of common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

    # List all files in the folder
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                 os.path.isfile(os.path.join(folder_path, f))]

    # Filter only those files with image extensions
    image_files = [f for f in all_files if os.path.splitext(f)[1].lower() in image_extensions]

    return sorted(image_files, key=lambda x: int(x.split('/')[-1].split('.')[0]))


def map_continuous_ais(ais, total):
    ais_map = {}
    for idx, l in enumerate(ais):
        for element in l:
            mmsi = element['mmsi']
            if mmsi in ais_map:
                ais_map[mmsi].append(idx)
            else:
                ais_map[mmsi] = [idx]

    # remove duplicates
    for mmsi, v in ais_map.items():
        ais_map[mmsi] = sorted(list(set(v)))

    ais_cont = {}
    for mmsi, v in ais_map.items():
        ais_cont[mmsi] = []
        first = v[0]
        last = v[-1]
        for i in range(total):
            if i <= first:  # reconstructing AIS information before we see the first AIS
                if len(v) > 1:  # this case we take the first and second AIS point and go backward in frames to estimate a linear position
                    first_ais_l = ais[v[0]]
                    next_ais_l = ais[v[1]]

                    for e in first_ais_l:
                        if e['mmsi'] == mmsi:
                            first_ais = e
                    for e in next_ais_l:
                        if e['mmsi'] == mmsi:
                            next_ais = e
                    if v[1] == v[0]:
                        pass
                    lon_steps = (float(first_ais['lon']) - float(next_ais['lon'])) / (v[1] - v[0])
                    lat_steps = (float(first_ais['lat']) - float(next_ais['lat'])) / (v[1] - v[0])
                    speed_steps = (float(first_ais['speed']) - float(next_ais['speed'])) / (v[1] - v[0])
                    steps = v[0] - i
                    ais_cont[mmsi].append((float(first_ais['lat']) + lat_steps * steps,
                                           float(first_ais['lon']) + lon_steps * steps,
                                           float(first_ais['speed']) + speed_steps * steps))
                else:  # if we only have one AIS point then we replicate that point over all the frames
                    elements = ais[first]
                    for e in elements:
                        if e['mmsi'] == mmsi:
                            ais_cont[mmsi].append((e['lat'], e['lon'], e['speed']))

            elif i >= last:  # recnstructing AIS after we see the last AIS in the frames
                if len(v) > 1:  # this case we take the first and second AIS point and go backward in frames to estimate a linear position
                    first_ais_l = ais[v[-2]]
                    next_ais_l = ais[v[-1]]

                    for e in first_ais_l:
                        if e['mmsi'] == mmsi:
                            first_ais = e
                    for e in next_ais_l:
                        if e['mmsi'] == mmsi:
                            next_ais = e
                    lon_steps = (float(next_ais['lon']) - float(first_ais['lon'])) / (v[1] - v[0])
                    lat_steps = (float(next_ais['lat']) - float(first_ais['lat'])) / (v[1] - v[0])
                    speed_steps = (float(next_ais['speed']) - float(first_ais['speed'])) / (v[1] - v[0])
                    steps = i - v[-1]
                    ais_cont[mmsi].append((float(next_ais['lat']) + lat_steps * steps,
                                           float(next_ais['lon']) + lon_steps * steps,
                                           float(next_ais['speed']) + speed_steps * steps))
                else:
                    elements = ais[last]
                    for e in elements:
                        if e['mmsi'] == mmsi:
                            ais_cont[mmsi].append((e['lat'], e['lon'], e['speed']))
            else:  # reconstructing the caps between AIS-data
                limits = find_limits(v, i)
                first_ais_l = ais[limits[0]]
                for e in first_ais_l:
                    if e['mmsi'] == mmsi:
                        first_ais = e
                next_ais_l = ais[limits[1]]
                for e in next_ais_l:
                    if e['mmsi'] == mmsi:
                        next_ais = e
                lon_steps = (float(next_ais['lon']) - float(first_ais['lon'])) / (limits[1] - limits[0])
                lat_steps = (float(next_ais['lat']) - float(first_ais['lat'])) / (limits[1] - limits[0])
                speed_steps = (float(next_ais['speed']) - float(first_ais['speed'])) / (limits[1] - limits[0])
                steps = i - limits[0]
                ais_cont[mmsi].append((float(first_ais['lat']) + lat_steps * steps,
                                       float(first_ais['lon']) + lon_steps * steps,
                                       float(first_ais['speed']) + speed_steps * steps))

    return ais_cont


def is_in_range(value):
    return -180 <= value <= 180


def magic_mf(path):
    camera_matrix, dist_coeffs = load_camera_m('camera_settings/MultiMatrix_CU81.npz')

    gps, orientation, ais = parse_json(path)
    rgb_img = list_images_in_folder(path + '/rgb')
    nir_img = list_images_in_folder(path + '/nir')

    if not os.path.exists(path + '/process'):
        os.makedirs(path + '/process')

    cont_ais = map_continuous_ais(ais, len(rgb_img))

    # let the party start
    for idx in range(len(rgb_img)):
        camera_c = gps[idx]
        camera_h = camera_c['alt']
        # Transforms ddmm.mmmm to dd.mmmm Data now comes in dd.mmmm so noneed to do anymore. leaving this just in case..
        # camera_c = (NMEA_to_decimal_degrees(camera_c['lat']), NMEA_to_decimal_degrees(camera_c['lon']))
        camera_c = ((camera_c['lat']), (camera_c['lon']))
        euler = orientation[idx]
        # transform coordinates from sensor to world coordinates.
        # reference, 0 degrees when camera looking east
        euler['x'] = 270 - euler['x'] + 10
        euler['y'] = -euler['y']
        euler['z'] = euler['z'] - 2

        img = cv.imread(rgb_img[idx])

        for mmsi_ref, positions in cont_ais.items():
            if mmsi_ref == '440016770':
                # AAIS for ulsan ship. We skip our own ship.
                continue
            position = positions[idx]
            ship_c = (float(position[0]), float(position[1]))
            # sometimes AIS record latitudes bigger than 180. Skippe that
            if not is_in_range(ship_c[0]) or not is_in_range(ship_c[1]):
                continue
            speed = float(position[2])
            # 440327630 ship visible
            # 441367000 behind camera
            if mmsi_ref == '440065990':
                pass
            proj_2d, distance, on_frame = projection_baby(camera_matrix, dist_coeffs, camera_c, ship_c,
                                                          (euler['x'], euler['y'], euler['z']), camera_h)
            if on_frame:
                continue
            # if the distance to the ship is bigger than 4km skippe.
            if distance > 4000:
                continue
            try:
                if mmsi_ref != '440016770':
                    for point in proj_2d.astype(int):
                        pos = (point[0][0], point[0][1])
                        img = cv.circle(img, pos, 50, 255, 2)
                        cv.putText(img, str(mmsi_ref), (pos[0] - 80, pos[1] - 50), cv.FONT_HERSHEY_SIMPLEX, 0.9,
                                   (36, 255, 12),
                                   2)
            except:
                print('error printing circle')
        cv.imwrite(path + '/process/' + str(idx) + '.jpg', img)


def list_folders(path):
    return [f.name for f in os.scandir(path) if f.is_dir()]


if __name__ == '__main__':
    # path = '/home/patrick/Data/Incheon/dataset'
    #
    # folders = list_folders(path)
    #
    # for folder in folders:
    #     to_process = path + '/' + folder
    #     magic_mf(to_process)

    path = '/home/patrick/Data/Incheon/dataset/1700460994'
    magic_mf(path)
