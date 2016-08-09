#! /usr/bin/env python
# -*- coding:utf-8 -*-

from binary_reader import *
from bcdn import *


class DBF :
    
    def __init__ (self, fname) :
        print fname
        self.fname = fname
        self.br = BinaryReader(fname)
        self.header = DBFHeader(self.br)
        self.header.printHeader()
        self.fields = self.readFields()
        self.printFields()
        self.records = self.readRecords()
        self.printRecords()

    def readFields (self) :
        fields = []
        length = (self.header.header_length - DBFHeader.LENGTH - 1) / 32
        for i in range(length) :
            fields.append(DBFField(self.br))
        unused = self.br.readByteAsNumber()
        return fields

    def readRecords (self) :
        records = []
        for i in range(min((10, self.header.num_records))) :
            record  = {}
            record['deleted_flag'] = self.br.readString(1)
            for field in self.fields :
                if field.field_type == 'C' :
                    record[field.field_name] = self.br.readString(field.field_length)
                elif field.field_type == 'N' :
                    record[field.field_name] = str(BCDN(self.br, field.field_length))
            records.append(record)
        return records

    def printFields (self) :
        print '    Fields        :'
        for field in self.fields :
            print '        ' + str(field)

    def printRecords (self) :
        print '    Records       :'
        for record in self.records :
            for key, value in record.items() :
                print '        {0:30s} {1:30s}'.format(key, value)
            print
        print


class DBFHeader :

    LENGTH = 32
    
    def __init__ (self, br) :
        self.flags = br.readByteAsNumber()
        self.year  = br.readByteAsNumber()
        self.month = br.readByteAsNumber()
        self.mday  = br.readByteAsNumber()
        self.num_records = br.readIntAsLittle()
        self.header_length = br.readShortAsLittle()
        self.record_length = br.readShortAsLittle()
        for i in range(2) :
            unused = br.readByteAsNumber()
        self.transaction = br.readByteAsNumber()
        self.encryption  = br.readByteAsNumber()
        for i in range(12) :
            unused = br.readByteAsNumber()
        self.mdx_flag = br.readByteAsNumber()
        self.lang_driver_id = br.readByteAsNumber()
        for i in range(2) :
            unused = br.readByteAsNumber()

    def printHeader (self) :
        print '    Flags         : {0:08b}'.format(self.flags)
        print '    Updated At    : {0:02d}-{1:02d}-{2:02d}'.format(self.year, self.month, self.mday)
        print '    Num Records   : {0:d}'.format(self.num_records)
        print '    Header Length : {0:d}'.format(self.header_length)
        print '    Record Length : {0:d}'.format(self.record_length)


class DBFField :
    
    def __init__ (self, br) :
        self.field_name = br.readString(10)
        unused = br.readByteAsNumber()
        self.field_type = br.readString(1)
        unused = br.readIntAsBig()
        self.field_length = br.readByteAsNumber()
        self.decimal_length = br.readByteAsNumber()
        unused = br.readShortAsBig()
        self.workspace_id = br.readByteAsNumber()
        for i in range(10) :
            unused = br.readByteAsNumber()
        self.mdx_flag = br.readByteAsNumber()

    def __str__ (self) :
        form = 'DBFField(type={1:s}, length={2:2d}, name={0:s})'
        return form.format(self.field_name, self.field_type, self.field_length)

