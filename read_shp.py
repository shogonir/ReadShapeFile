#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import struct
import pickle

from PIL import Image


class BinaryReader :
    
    def __init__ (self, fname) :
        self.fname = fname
        try :
            self.fp = open(fname, 'rb')
        except IOError :
            self.__del__()

    def __del__ (self) :
        self.fp.close()

    def readByteAsNumber (self) :
        return ord(self.fp.read(1))

    def readIntAsBig (self) :
        result = 0
        for i in range(4) :
            result *= 2 ** 8
            result += self.readByteAsNumber()
        return result

    def readIntAsLittle (self) :
        byte_list = []
        for i in range(4) :
            byte_list.append(self.readByteAsNumber())
        hex_string = struct.pack('BBBB', *byte_list)
        return struct.unpack('i', hex_string)[0]

    def readShortAsBig (self) :
        result = 0
        for i in range(2) :
            result *= 2 ** 8
            result += self.readByteAsNumber()
        return result

    def readShortAsLittle (self) :
        byte_list = []
        for i in range(2) :
            byte_list.append(self.readByteAsNumber())
        hex_string = struct.pack('BB', *byte_list)
        return struct.unpack('H', hex_string)[0]

    def readDoubleAsLittle (self) :
        byte_list = []
        for i in range(8) :
            byte_list.append(self.readByteAsNumber())
        hex_string = struct.pack('BBBBBBBB', *byte_list)
        return struct.unpack('d', hex_string)[0]

    def readString (self, num_characters) :
        byte_list = []
        for i in range(num_characters) :
            byte_list.append(self.readByteAsNumber())
        return ''.join(map(chr, byte_list))


class ShapeMain :

    LENGTH_RECORD_HEADER = 4
    
    def __init__ (self, fname) :
        print fname
        self.fname = fname
        self.br = BinaryReader(fname)
        self.header  = ShapeMainHeader(self.br)
        self.header.printHeader()
        self.records = self.readRecords()
        self.printInformation()

    def __del__ (self) :
        self.br.__del__()

    def printInformation (self) :
        print '    Records     :'
        for recordno, record in enumerate(self.records) :
            print '        ' + str(record.content)
            if recordno == 9 :
                print '        ...   there are {0:d} records'.format(len(self.records))
                break
        print

    def readRecords (self) :
        records = []
        file_length = self.header.file_length - 50
        while file_length > 0 :
            record = ShapeMainRecord(self.br, self.header.shape_type)
            if record.content == None :
                break
            records.append(record)
            file_length -= self.LENGTH_RECORD_HEADER + record.content.length
        return records


class ShapeMainHeader :
    
    def __init__ (self, br) :
        self.file_code = br.readIntAsBig()
        for i in range(5) :
            unused = br.readIntAsBig()
        self.file_length = br.readIntAsBig()
        self.version = br.readIntAsLittle()
        self.shape_type = br.readIntAsLittle()
        self.xmin = br.readDoubleAsLittle()
        self.ymin = br.readDoubleAsLittle()
        self.xmax = br.readDoubleAsLittle()
        self.ymax = br.readDoubleAsLittle()
        self.zmin = br.readDoubleAsLittle()
        self.zmax = br.readDoubleAsLittle()
        self.mmin = br.readDoubleAsLittle()
        self.mmax = br.readDoubleAsLittle()

    def printHeader (self) :
        print '    File Code   : {0:6d}'.format(self.file_code)
        print '    File Length : {0:6d}'.format(self.file_length)
        print '    Version     : {0:6d}'.format(self.version)
        print '    Shape Type  : {0:6d}'.format(self.shape_type)
        print '    Xmin        : {0:f}'.format(self.xmin)
        print '    Xmax        : {0:f}'.format(self.xmax)
        print '    Ymin        : {0:f}'.format(self.ymin)
        print '    Ymax        : {0:f}'.format(self.ymax)


class ShapeMainRecord :

    SHAPE_TYPE_POINT = 1
    SHAPE_TYPE_POLY_LINE = 3
    SHAPE_TYPE_POLYGON = 5

    def __init__ (self, br, shape_type) :
        self.br = br
        self.shape_type = shape_type
        self.number  = br.readIntAsBig()
        self.length  = br.readIntAsBig()
        self.content = self.readRecordContent()

    def readRecordContent (self) :
        if self.shape_type == self.SHAPE_TYPE_POINT :
            return ShapeMainPoint(self.br)
        elif self.shape_type == self.SHAPE_TYPE_POLY_LINE :
            return ShapeMainPolyLine(self.br)
        elif self.shape_type == self.SHAPE_TYPE_POLYGON :
            return ShapeMainPolygon(self.br)
        return None

    def assertShapeType (self, shape_type, correct_shape_type) :
        if shape_type != correct_shape_type :
            form = 'ASSERTION WARNING : shape type should be {0:d}, given {1:d}'
            print form.format(correct_shape_type, shape_type)


class ShapeMainPoint (ShapeMainRecord) :

    LENGTH = 10

    def __init__ (self, br) :
        shape_type = br.readIntAsLittle()
        self.x = br.readDoubleAsLittle()
        self.y = br.readDoubleAsLittle()
        self.length = 10
        self.assertShapeType(shape_type, ShapeMainRecord.SHAPE_TYPE_POINT)

    def __str__ (self) :
        return 'ShapeMainPoint(X={0:f}, Y={1:f})'.format(self.x, self.y)


class ShapeMainPolyLine (ShapeMainRecord) :
    
    def __init__ (self, br) :
        self.br = br
        shape_type = br.readIntAsLittle()
        self.box = BoundingBox(br)
        self.num_parts = br.readIntAsLittle()
        self.num_points = br.readIntAsLittle()
        self.parts = self.readParts()
        self.points = self.readPoints()
        self.length  = 2 + BoundingBox.LENGTH
        self.length += self.num_parts * 2 + 4
        self.length += self.num_points * Point.LENGTH
        self.assertShapeType(shape_type, ShapeMainRecord.SHAPE_TYPE_POLY_LINE)

    def readParts (self) :
        parts = []
        for i in range(self.num_parts) :
            parts.append(self.br.readIntAsLittle())
        return parts

    def readPoints (self) :
        points = []
        for i in range(self.num_points) :
            points.append(Point(self.br))
        return points

    def __str__ (self) :
        form = 'ShapeMainPolyLine(num_parts={0:d}, num_points={1:d})'
        return form.format(self.num_parts, self.num_points)


class ShapeMainPolygon (ShapeMainRecord) :
    
    def __init__ (self, br) :
        self.br = br
        shape_type = br.readIntAsLittle()
        self.box = BoundingBox(br)
        self.num_parts = br.readIntAsLittle()
        self.num_points = br.readIntAsLittle()
        self.parts = self.readParts()
        self.points = self.readPoints()
        self.length  = 2 + self.box.length + 2 + 2
        self.length += 2 * self.num_parts
        self.length += Point.LENGTH * self.num_points
        self.assertShapeType(shape_type, ShapeMainRecord.SHAPE_TYPE_POLYGON)

    def readParts (self) :
        parts = []
        for i in range(self.num_parts) :
            parts.append(self.br.readIntAsLittle())
        return parts

    def readPoints (self) :
        points = []
        for i in range(self.num_points) :
            points.append(Point(self.br))
        return points

    def __str__ (self) :
        form = 'ShapeMainPolygon(num_parts={0:d}, num_points={1:d})'
        return form.format(self.num_parts, self.num_points)


class ShapeIndex :
    
    def __init__ (self, fname) :
        print fname
        self.fname = fname
        self.br = BinaryReader(fname)
        self.header = ShapeMainHeader(self.br)
        self.header.printHeader()
        self.records = self.readRecords()
        self.printRecords()

    def readRecords (self) :
        records = []
        length = self.header.file_length - 50
        while length > 0 :
            record = Index(self.br)
            records.append(record)
            length -= record.length
        return records

    def printRecords (self) :
        print '    Records     :'
        for recordno, record in enumerate(self.records) :
            print '        ' + str(record)
            if recordno == 9 :
                print '        ... there are {0:d} records'.format(len(self.records))
                break
        print


class Index :

    LENGTH = 4
    
    def __init__ (self, br) :
        self.key = br.readIntAsBig()
        self.value = br.readIntAsBig()
        self.length = self.LENGTH

    def __str__ (self) :
        form = 'Index(key={0:d}, value={1:d})'
        return form.format(self.key, self.value)


class BoundingBox :

    LENGTH = 16
    
    def __init__ (self, br) :
        self.xmin = br.readDoubleAsLittle()
        self.ymin = br.readDoubleAsLittle()
        self.xmax = br.readDoubleAsLittle()
        self.ymax = br.readDoubleAsLittle()
        self.length = 16


class Point :
    
    LENGTH = 8

    def __init__ (self, br) :
        self.x = br.readDoubleAsLittle()
        self.y = br.readDoubleAsLittle()
        self.length = self.LENGTH


class Vector2 :
    
    def __init__ (self, x, y) :
        self.x = x
        self.y = y


class PngCreator :
    
    @staticmethod
    def createFromShapeMains (shapes) :
        ratio = 40000
        xmin, xmax, ymin, ymax = PngCreator.extractMinMax(shapes)
        width  = int(ratio * (xmax - xmin)) + 1
        height = int(ratio * (ymax - ymin)) + 1
        image  = Image.new('RGB', (width, height), (0x00, 0x00, 0x00))
        for shape in shapes :
            approved_types = [ShapeMainRecord.SHAPE_TYPE_POLY_LINE, ShapeMainRecord.SHAPE_TYPE_POLYGON]
            if shape.header.shape_type in approved_types :
                for record in shape.records :
                    for pointno, point in enumerate(record.content.points) :
                        if pointno != 0 :
                            point1 = PngCreator.normalizePoint(pre_point, xmin, xmax, ymin, ymax, width, height)
                            point2 = PngCreator.normalizePoint(point,     xmin, xmax, ymin, ymax, width, height)
                            line = PngCreator.drawLine(point1, point2)
                            for p in line :
                                if 0 <= p.x and p.x < width and 0 <= p.y and p.y < height :
                                    image.putpixel((p.x, p.y), (0xFF, 0xFF, 0xFF))
                        pre_point = point
        image.show()

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

if __name__ == '__main__' :
    
    dname = '544022'
    files = os.listdir(dname)
    
    dbfs, shxs, shps, prjs = [], [], [], []
    for fname in files :
        extension = fname.split('.')[1]
        exec('{0:s}s.append(dname + "/" + fname)'.format(extension))
    
    shapes = [ShapeMain(fname) for fname in shps]

    PngCreator.createFromShapeMains(shapes)

