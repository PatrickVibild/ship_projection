import numpy as np
import cv2 as cv
from scipy.spatial.transform import Rotation as R

from distance_test import NMEA_to_decimal_degrees, distance_between_coordinates


def load_camera_m(file_name):
    with (np.load(file_name) as X):
        camMatrix = X['camMatrix']
        distCoef = X['distCoef']
        # rVector = X['rVector']
        # tVector = X['tVector']
        return camMatrix, distCoef


def rotvec_from_euler(x, y, z):
    # we take into consideration the opencv coord system.
    r = R.from_euler('xyz', [z, x, y], degrees=True)
    return r.as_rotvec()


def tvec_camera(height):
    tvec = np.zeros((3, 1), np.float32)
    tvec[2][0] = np.float32(height)
    return tvec


def xyz_to_opencv_coord(x, y, z):
    # https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/OWENS/LECT9/node2.html
    # transforming world coordinates to OpenCV coordinate system
    return np.array([[-y, z, x]], np.float32)





def projection_baby(camera_matrix, dist_coeffs, camera_c, ship_c, orientation, height):
    rvec = rotvec_from_euler(orientation[0], orientation[1], orientation[2])
    tvec = tvec_camera(0)
    # https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/OWENS/LECT9/node2.html
    distance, x, y = distance_between_coordinates(camera_c, ship_c)
    points_3d = xyz_to_opencv_coord(x, y, height)

    points_2d, _ = cv.projectPoints(points_3d,
                                    rvec, tvec,
                                    camera_matrix,
                                    dist_coeffs)
    return points_2d, distance


if __name__ == '__main__':
    camera_matrix, dist_coeffs = load_camera_m('camera_settings/MultiMatrix_CU81.npz')

    # sensor info
    camera_c = (3727.26271, 12635.4682)
    camera_c = (NMEA_to_decimal_degrees(camera_c[0]), NMEA_to_decimal_degrees(camera_c[1]))
    print('Camera position: ' + str(camera_c) + '\n')
    print('Camera Matrix: \n' + str(camera_matrix) + '\n')
    camera_h = 4

    c_t = (3727.27457, 12635.46824)
    c_t = (NMEA_to_decimal_degrees(c_t[0]), NMEA_to_decimal_degrees(c_t[1]))
    c_t2 = (3727.25368, 12635.48112)
    c_t2 = (NMEA_to_decimal_degrees(c_t2[0]), NMEA_to_decimal_degrees(c_t2[1]))

    # tanker
    ship_tanker = (37.448312, 126.5781)  # in frame ship contanier
    # tug1
    ship_tug1 = (37.450693, 126.577617)
    ship_tug2 = (37.4509, 126.58565)
    ship_tug3 = (37.448635, 126.578202)


    #euler = ((63.3125), -0.4375, 0.0625)
    euler = (207,0,0)
    points_2d_tanker = projection_baby(camera_matrix, dist_coeffs, camera_c, ship_tanker, euler, camera_h)
    points_2d_t1 = projection_baby(camera_matrix, dist_coeffs, camera_c, ship_tug1, euler, camera_h)
    points_2d_t2 = projection_baby(camera_matrix, dist_coeffs, camera_c, ship_tug2, euler, camera_h)
    points_2d_t3 = projection_baby(camera_matrix, dist_coeffs, camera_c, ship_tug3, euler, camera_h)
    # if 0 < points_2d[0][0][0] < 1920 and 0 < points_2d[0][0][1] < 1080:

    print()
    # Plot 2D points
    #                 img = np.zeros((1080, 1920),
    #                                dtype=np.uint8)
    img = cv.imread('1.jpg')

    for point in points_2d_tanker.astype(int):
        pos = (point[0][0], point[0][1])
        img = cv.circle(img, pos, 25, 255, -1)
    for point in points_2d_t1.astype(int):
        pos = (point[0][0], point[0][1])
        img = cv.circle(img, pos, 25, 255, -1)
    for point in points_2d_t2.astype(int):
        pos = (point[0][0], point[0][1])
        img = cv.circle(img, pos, 25, 255, -1)
    for point in points_2d_t3.astype(int):
        pos = (point[0][0], point[0][1])
        img = cv.circle(img, pos, 25, 255, -1)

    cv.imshow('Image', img)
    cv.waitKey(0)
    cv.destroyAllWindows()
