#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import struct


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

    def readDoubleAsLittle (self) :
        byte_list = []
        for i in range(8) :
            byte_list.append(self.readByteAsNumber())
        hex_string = struct.pack('BBBBBBBB', *byte_list)
        return struct.unpack('d', hex_string)[0]


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
        print '    Ymin        : {0:f}'.format(self.ymin)
        print '    Xmax        : {0:f}'.format(self.xmax)
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


if __name__ == '__main__' :
    
    dname = '544022'
    files = os.listdir(dname)
    
    dbfs, shxs, shps, prjs = [], [], [], []
    for fname in files :
        extension = fname.split('.')[1]
        exec('{0:s}s.append(dname + "/" + fname)'.format(extension))
    
    for shp_name in shps :
        shp_file = ShapeMain(shp_name)

    for shx_name in shxs :
        shx_file = ShapeIndex(shx_name)
