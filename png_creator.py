#! /usr/bin/env python
# -*- coding:utf-8 -*-

from PIL import Image

from shape_main import *


class PngCreator :
    
    @staticmethod
    def createFromShapeMains (shapes) :
        ratio = 40000
        xmin, xmax, ymin, ymax = PngCreator.extractMinMax(shapes)
        width  = int(ratio * (xmax - xmin)) + 1
        height = int(ratio * (ymax - ymin)) + 1
        image  = Image.new('RGB', (width, height), (0x00, 0x00, 0x00))
        approved_types = [ShapeMainRecord.SHAPE_TYPE_POLY_LINE, ShapeMainRecord.SHAPE_TYPE_POLYGON]
        for shape in shapes :
            color = PngCreator.prefixToColor(shape.fname.split('-')[3])
            if shape.header.shape_type in approved_types :
                for record in shape.records :
                    for pointno, point in enumerate(record.content.points) :
                        if pointno != 0 :
                            point1 = PngCreator.normalizePoint(pre_point, xmin, xmax, ymin, ymax, width, height)
                            point2 = PngCreator.normalizePoint(point,     xmin, xmax, ymin, ymax, width, height)
                            line = PngCreator.drawLine(point1, point2)
                            for p in line :
                                if 0 <= p.x and p.x < width and 0 <= p.y and p.y < height :
                                    image.putpixel((p.x, p.y), color)
                        pre_point = point
        image.show()

    @staticmethod
    def prefixToColor (prefix) :
        if 'Rail' in prefix :
            return (0xFF, 0x00, 0xFF)
        elif 'Rvr' in prefix :
            return (0x00, 0xFF, 0xFF)
        elif 'Adm' in prefix :
            return (0xFF, 0xFF, 0x00)
        elif 'Cntr' in prefix :
            return (0x00, 0xFF, 0x00)
        elif 'Bld' in prefix :
            return (0xAA, 0xAA, 0x00)
        elif 'Rd' in prefix :
            return (0xFF, 0x00, 0x00)
        return (0xFF, 0xFF, 0xFF)

    @staticmethod
    def normalizePoint (point, xmin, xmax, ymin, ymax, width, height) :
        x = int(1.0 * width  * (point.x - xmin) / (xmax - xmin))
        y = int(1.0 * height * (point.y - ymin) / (ymax - ymin))
        return Vector2(x, y)

    @staticmethod
    def extractMinMax (shapes) :
        h0 = shapes[0].header
        xmin, xmax, ymin, ymax = h0.xmin, h0.xmax, h0.ymin, h0.ymax
        for shape in shapes :
            xmin = shape.header.xmin if shape.header.xmin < xmin else xmin
            xmax = shape.header.xmax if shape.header.xmax > xmax else xmax
            ymin = shape.header.ymin if shape.header.ymin < ymin else ymin
            ymax = shape.header.ymax if shape.header.ymax > ymax else ymax
        return xmin, xmax, ymin, ymax

    @staticmethod
    def drawLine (point1, point2) :
        points = []
        try :
            slope = 1.0 * (point2.y - point1.y) / (point2.x - point1.x)
            if abs(slope) > 1.0 :
                top, bottom = (point1, point2) if point1.y > point2.y else (point2, point1)
                for y in range(bottom.y, top.y + 1) :
                    progress = 1.0 * (y - bottom.y) / (top.y - bottom.y)
                    x = int(bottom.x + progress * (top.x - bottom.x))
                    points.append(Vector2(x, y))
            else :
                right, left = (point1, point2) if point1.x > point2.x else (point2, point1)
                for x in range(left.x, right.x + 1) :
                    progress = 1.0 * (x - left.x) / (right.x - left.x)
                    y = int(left.y + progress * (right.y - left.y))
                    points.append(Vector2(x, y))
        except ZeroDivisionError :
            pass
        return points

