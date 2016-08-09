#! /usr/bin/env python
# -*- coding:utf-8 -*-


# Binary Coded Decimal Numeric
class BCDN :
    
    def __init__ (self, br, length) :
        self.byte_list = []
        for i in range(length) :
            self.byte_list.append(br.readByteAsNumber())

    def __str__ (self) :
        return ''.join([BCDN.byteToString(byte) for byte in self.byte_list])

    @staticmethod
    def byteToString (byte) :
        return BCDN.fourBitsToDecimal(byte/(2**4)) + BCDN.fourBitsToDecimal(byte%(2**4))

    @staticmethod
    def fourBitsToDecimal (bits) :
        if bits < 10 :
            return str(bits)
        elif bits == 10 :
            return '.'
        elif bits == 11 :
            return '-'
        else :
            return '?'
