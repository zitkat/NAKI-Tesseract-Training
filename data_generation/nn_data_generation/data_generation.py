#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Training data generation w/o background map
Each character has its own map generated
Input: Synthetic png files + json files with annotations
Output: Target map for each character
"""


#vygenerovani target dat pro trenovani neuronove site, bez mapy pro pozadi

import h5py
import os
import cv2
import pickle
import numpy as np

input_dir_path = "//147.228.125.178/home/Generated_texts/noisy_04_NEW/"
input_img_path = input_dir_path + "images/"
input_pckl_path = input_dir_path + "pg_pickle/"
img_lst = os.listdir(input_img_path)
pickle_lst = os.listdir(input_pckl_path)
img_lst.sort()
pickle_lst.sort()
output_path = "./h5py/"
char_wanted = ['!', '"', '&',  "'", '(', ')', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '=', '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z', '[', ']', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '|', '§', 'Á', 'É', 'Í', 'Ú', 'Ý', 'á', 'é', 'í', 'ó', 'ú', 'ý', 'Č', 'č', 'ď', 'Ě', 'ě', 'ň', 'Ř', 'ř', 'Š', 'š', 'ť', 'ů', 'Ž', 'ž', '—', '“', '„']
f_out = h5py.File(output_path + "maps2.h5", 'w')

chunk_size = 1
chunk_batch = 1
index_dataset = 0
w = 620
h = 876

data = f_out.create_dataset('data', shape=(chunk_size, 1, h, w), maxshape=(None, 1, h, w), dtype=np.float32)
label = f_out.create_dataset('label', shape=(chunk_size, len(char_wanted), h, w), maxshape=(None, len(char_wanted), h, w), dtype=int)

def generate_maps(loaded_file, char_wanted): #original maps generation
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
                            pole[y, x, char_channel] = 255 #zmena z 1 na 255 z duvodu pozdejsiho resizu na 25% velikosti

    return pole

# def generate_maps(loaded_file, char_wanted):  #generating maps with convex hulls, fucking slow!!!
#
#     # loaded_file = pickle.load(open(pickle_file,'rb'))
#
#     pole = np.zeros((loaded_file.resolution_h, loaded_file.resolution_w, len(char_wanted)),dtype=np.uint8)
#
#     for box in loaded_file.boxes:
#         for line in box.lines:
#             for word in line.words:
#                 for char in word.characters:
#                     if char.character in char_wanted:
#                         char_channel = char_wanted.index(char.character)
#                         zz = np.zeros((loaded_file.resolution_h, loaded_file.resolution_w),dtype=np.uint8)
#                         cv2.fillConvexPoly(zz,cv2.convexHull(char.pixels_yx),255)
#                         pole[:, :, char_channel] += zz
#
#     return pole

for i in range (500,600):
    img = cv2.imread(input_img_path + img_lst[i],0)
    img = cv2.resize(img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_CUBIC)
    img = img.astype('float32') / 255.
    file = input_pckl_path + ''.join(pickle_lst[i:i + 1])
    loaded_pickle = pickle.load(open(file, "rb"))
    maps = generate_maps(loaded_pickle, char_wanted)
    maps= maps.transpose(2,0,1)
    resized_maps = np.zeros((len(char_wanted), h, w), dtype=np.int)
    for j in range(0,len(char_wanted)):
        resized_maps[j,:,:] = cv2.resize(maps[j,:, ], (0,0), fx=0.25, fy=0.25)
    resized_maps = resized_maps>50
    if index_dataset == chunk_batch * chunk_size:
        chunk_batch += 1
        data.resize(chunk_batch * chunk_size, axis=0)
        label.resize(chunk_batch * chunk_size, axis=0)

    data[index_dataset, :] = img
    label[index_dataset, :] = resized_maps
    index_dataset += 1
    print("Soubor: "+ img_lst[i] + " byl zpracovan a ulozen do h5.")

f_out.close()
print('Hotovo!')





