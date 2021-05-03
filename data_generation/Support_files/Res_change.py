#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Resolution change
"""

import cv2

dir_path = "./res_change/"


img = cv2.imread(dir_path+"img.png",1)
img2 = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
cv2.imwrite(dir_path+'img2.png',img2)
img3 = cv2.resize(img, None, fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)
cv2.imwrite(dir_path+'img3.png',img3)
img4 = cv2.resize(img, None, fx=0.2, fy=0.2, interpolation = cv2.INTER_CUBIC)
cv2.imwrite(dir_path+'img4.png',img4)
img5 = cv2.resize(img, None, fx=0.15, fy=0.15, interpolation = cv2.INTER_CUBIC)
cv2.imwrite(dir_path+'img5.png',img5)
img6 = cv2.resize(img, None, fx=0.1, fy=0.1, interpolation = cv2.INTER_CUBIC)
cv2.imwrite(dir_path+'img6.png',img6)