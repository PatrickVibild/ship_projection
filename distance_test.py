from haversine import haversine, Unit
import math


def NMEA_to_decimal_degrees(x):
    degrees = int(x) // 100
    minutes = x - 100 * degrees
    return degrees + minutes / 60


def distance_between_coordinates(c1, c2):
    x = haversine(c1, (c1[0], c2[1]), Unit.METERS)
    if c1[1] > c2[1]:
        x = -x
    y = haversine(c1, (c2[0], c1[1]), Unit.METERS)
    if c1[0] > c2[0]:
        y = -y
    dist = haversine(c1, c2, Unit.METERS)
    return dist, x, y


if __name__ == '__main__':
    # distance in DDDMM.MMMM format
    d1 = (3527.42864, 12921.56825)
    d1_decimal = (NMEA_to_decimal_degrees(d1[0]), NMEA_to_decimal_degrees(d1[1]))
    print(d1_decimal)
    d1 = d1_decimal

    d2 = (35.447088, 129.367275)

    abs_dist, x_d, y_d = distance_between_coordinates(d1, d2)

    print(x_d)
    print(y_d)
    print(abs_dist)
