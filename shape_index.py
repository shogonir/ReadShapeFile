#! /usr/bin/env pyhton
# -*- coding:utf-8 -*-


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

