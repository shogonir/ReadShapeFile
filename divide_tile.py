#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import math
from PIL import Image


L = 85.05112878
lon_min, lat_min, lon_max, lat_max = 140.25, 36.16666, 140.291666667, 36.208333333

class Point :
    
    def __init__ (self, x, y) :
        self.x = x
        self.y = y

def x_from_lon_and_z (lon, z) :
    return 2 ** (z+7) * (lon / 180.0 + 1.0)

def y_from_lat_and_z (lat, z) :
    max_sin_y = math.sin(  L / 180.0 * math.pi)
    sin_y     = math.sin(lat / 180.0 * math.pi)
    return 2 ** (z+7) / math.pi * (math.atanh(max_sin_y) - math.atanh(sin_y))

def lon_from_x_and_z (x, z) :
    return 180.0 * (float(x) / (2 ** (z+7)) - 1)

def lat_from_y_and_z (y, z) :
    max_sin = math.sin(math.pi / 180.0 * L)
    angle   = math.pi / 2 ** (z+7) * y
    return 180.0 / math.pi * (math.asin(math.tanh(math.atanh(max_sin) - angle)))

def draw_line (image, p1, p2, width, height) :
    try :
        slope = 1.0 * (p2.y - p1.y) / (p2.x - p1.x if p1.x!=p2.x else 1)
        if abs(slope) > 1.0 :
            top, bottom = (p1, p2) if p1.y > p2.y else (p2, p1)
            for y in range(bottom.y, top.y + 1) :
                div = top.y - bottom.y if top.y != bottom.y else 1
                progress = 1.0 * (y - bottom.y) / div
                x = int(bottom.x + progress * (top.x - bottom.x))
                if 0 <= x and x < width and 0 <= y and y < height :
                    image.putpixel((x, y), (0xFF, 0xFF, 0xFF))
        else :
            right, left = (p1, p2) if p1.x > p2.x else (p2, p1)
            for x in range(left.x, right.x + 1) :
                div = right.x - left.x if right.x != left.x else 1
                progress = 1.0 * (x - left.x) / div
                y = int(left.y + progress * (right.y - left.y))
                if 0 <= x and x < width and 0 <= y and y < height :
                    image.putpixel((x, y), (0xFF, 0xFF, 0xFF))
    except ZeroDivisionError :
        pass

def xyz_point (x, y, z) :
    px = int(ratio * (lon_from_x_and_z(x, z) - lon_min))
    py = int(ratio * (lat_from_y_and_z(y, z) - lat_min))
    return Point(px, py)

if __name__ == '__main__' :
    
    ratio  = 10000.0
    width  = int(ratio * (lon_max - lon_min))
    height = int(ratio * (lat_max - lat_min))
    image  = Image.new('RGB', (width, height), (0x00, 0x00, 0x00))
    
    z = 10

    xmax = xmin = int(x_from_lon_and_z(lon_min, z))
    ymax = ymin = int(y_from_lat_and_z(lat_min, z))
    while lon_from_x_and_z(xmax, z) < lon_max :
        xmax += 1
    while lat_from_y_and_z(ymin, z) < lat_max :
        ymin -= 1
    
    for x in range(xmin, xmax) :
        for y in range(ymin, ymax + 1) :
            point1 = xyz_point(x  , y  , z)
            point2 = xyz_point(x+1, y  , z)
            point3 = xyz_point(x  , y+1, z)
            draw_line(image, point1, point2, width, height)
            draw_line(image, point1, point3, width, height)

    image.show()

