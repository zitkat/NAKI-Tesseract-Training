#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Checking h5py files.
"""

import cv2
import h5py
import numpy as np

char_wanted = ['!', '"', '&', "'", '(', ')', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '=', '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z', '[', ']', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '|', '§', 'Á', 'É', 'Í', 'Ú', 'Ý', 'á', 'é', 'í', 'ó', 'ú', 'ý', 'Č', 'č', 'ď', 'Ě', 'ě', 'ň', 'Ř', 'ř', 'Š', 'š', 'ť', 'ů', 'Ž', 'ž', '—', '“', '„']

with h5py.File("//147.228.125.178/home/h5py_convex/maps2.h5",'r') as fr:
    X = fr['data'][0:6]
    y = fr['label'][0:6]
print(X.shape)
print(y.shape)
print(len(fr))

for i in range(0,5):

    cv2.imshow('img', X[i,0,:,:])
    cv2.waitKey(1500)
    cv2.destroyAllWindows()
    maps = y[i,:,:,:]
    for j in range(0, y.shape[1]):
        cv2.imshow('map'+char_wanted[j], maps[j,:,:].astype(np.float32))
        # cv2.imwrite('pic'+str(j)+'.png', maps[j,:,:].astype(np.float32))
        cv2.waitKey(500)
        cv2.destroyAllWindows()