#!/usr/bin/env python

__author__ = "Ivan Gruber"
__credits__ = "Miroslav Hlavac"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Character masks generation
"""

import pickle
import numpy as np
import cv2



def generate_maps(loaded_file, char_wanted):

    # loaded_file = pickle.load(open(pickle_file,'rb'))

    pole = np.zeros((loaded_file.resolution_h, loaded_file.resolution_w, len(char_wanted)))

    for box in loaded_file.boxes:
        for line in box.lines:
            for word in line.words:
                for char in word.characters:
                    if char.character in char_wanted:
                        char_channel = char_wanted.index(char.character)
                        pix = char.pixels_yx
                        for i in range(0, pix.shape[0]):
                            y = pix[i, 0]
                            x = pix[i, 1]
                            pole[y, x, char_channel] = 1

    return pole


char_wanted = ['!', '"', '&', "'", '(', ')', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '=', '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z', '[', ']', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '|', '§', 'Á', 'É', 'Í', 'Ú', 'Ý', 'á', 'é', 'í', 'ó', 'ú', 'ý', 'Č', 'č', 'ď', 'Ě', 'ě', 'ň', 'Ř', 'ř', 'Š', 'š', 'ť', 'ů', 'Ž', 'ž', '—', '“', '„']
pf = r'E:\FileGenerator\data\outputs\pg_pickle\V_1945_BR_0024_gt_4_two_columns.pickle'
loaded_file = pickle.load(open(pf,'rb'))
img = generate_maps(loaded_file,char_wanted)

for i in range(img.shape[-1]):

    cv2.imshow('img', cv2.resize(img[:,:,i]*255, (0,0), fx=0.25, fy=0.25))
    cv2.waitKey()

