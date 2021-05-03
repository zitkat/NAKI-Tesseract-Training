#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Generated data check.
"""


import _pickle as pickle
import os.path
import numpy as np
import cv2

output_dir_path = "./data/outputs/"
output_pg_path = output_dir_path + "pg_pickle/"

pickle_lst = os.listdir(output_pg_path)
pickle_lst.sort()
poc = 0
for pick in pickle_lst:
    file = output_pg_path + pick
    print("Nazev souboru: "+file)
    loaded_file = pickle.load(open(file, "rb"))
    pole = np.zeros((loaded_file.resolution_h, loaded_file.resolution_w))
    for box in loaded_file.boxes:
        for line in box.lines:
            for word in line.words:
                for char in word.characters:
                    pix = char.pixels_yx
                    for i in range (0, pix.shape[0]):
                        y = pix[i,0]
                        x = pix[i,1]
                        pole[y,x] = 1
    cv2.imshow('img', pole*255)
    cv2.waitKey()

    poc +=1
    if poc ==2:
        break
cv2.imshow('img',pole)
cv2.imwrite('img.png',pole*255)
cv2.waitKey()
