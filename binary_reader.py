#! /usr/bin/env pyhton
# -*- coding:utf-8 -*-

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

