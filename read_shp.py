#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

from shape_main import *
from png_creator import *
from dbf import *

if __name__ == '__main__' :

    dname = '544022'
    files = os.listdir(dname)
    
    dbfs, shxs, shps, prjs = [], [], [], []
    for fname in files :
        extension = fname.split('.')[1]
        exec('{0:s}s.append(dname + "/" + fname)'.format(extension))
    
    shapes = [ShapeMain(fname) for fname in shps]

    PngCreator.createFromShapeMains(shapes)

    # dbfs = [DBF(fname) for fname in dbfs]

