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
    
    denied_prefixs = [
        'Cntr', 'VegeClassL', 'VLine', 'TrfStrct', 'TrfTnnlEnt', 'PwrPlnt', 'Cntr'
        'PwrTrnsmL', 'WA', 'WL', 'WoodRes', 'SpcfArea', 'AdmArea', 'AdmBdry', 'AdmPt'
    ]

    shapes = [ShapeMain(fname) for fname in shps if fname not in denied_prefixs]

    PngCreator.createFromShapeMains(shapes)

    # dbfs = [DBF(fname) for fname in dbfs]

