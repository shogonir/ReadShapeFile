#! /usr/bin/env python
# -*- coding:utf-8 -*-


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

