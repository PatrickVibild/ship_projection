import numpy as np
import cv2 as cv
from scipy.spatial.transform import Rotation as R
from haversine import haversine, Unit

def distance_between_coordinates(c1, c2):
    x = haversine(c1, (c1[0], c2[1]), Unit.METERS)
    if c1[1] > c2[1]:
        x = -x
    y = haversine(c1, (c2[0], c1[1]), Unit.METERS)
    if c1[1] > c2[1]:
        y = -y
    dist = haversine(c1, c2, Unit.METERS)
    return dist, x, y


def rotvec_from_euler(orientation):
    r = R.from_euler('xyz', [orientation[0], orientation[1], orientation[2]], degrees=True)
    return r.as_rotvec()


if __name__ == '__main__':
    camera_matrix = np.array([
        [1062.39, 0., 943.93],
        [0., 1062.66, 560.88],
        [0., 0., 1.]
        ])

    dist_coeffs = np.array([-0.33520254,  0.14872426,  0.00057997, -0.00053154, -0.03600385])

    camera_p = (37.4543785, 126.59113666666666)
    ship_p = (37.448312, 126.5781)

    # Other ships near to the previous one.
    # ship_p = (37.450693, 126.577617)
    # ship_p = (37.4509, 126.58565)
    # ship_p = (37.448635, 126.578202)
    camera_orientation = (206.6925, 0, 0) # Euler orientation.

    rvec = rotvec_from_euler(camera_orientation)
    tvec = np.zeros((3, 1), np.float32)

    _, x, y = distance_between_coordinates(camera_p, ship_p)
    points_3d = np.array([[[x, y, 0]]], np.float32)

    points_2d, _ = cv.projectPoints(points_3d,
                                    rvec, tvec,
                                    camera_matrix,
                                    dist_coeffs)
    print(points_2d)
