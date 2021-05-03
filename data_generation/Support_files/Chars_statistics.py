#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Character statistic calculation
"""

import _pickle as pickle
import os.path
import numpy as np

input_pckl_path = "//147.228.125.178/home/Generated_texts/noisy_04_NEW/pg_pickle/"
pickle_lst = os.listdir(input_pckl_path)
pickle_lst.sort()
char_wanted = ['!', '"', '&', "'", '(', ')', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '=', '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z', '[', ']', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '|', '§', 'Á', 'É', 'Í', 'Ú', 'Ý', 'á', 'é', 'í', 'ó', 'ú', 'ý', 'Č', 'č', 'ď', 'Ě', 'ě', 'ň', 'Ř', 'ř', 'Š', 'š', 'ť', 'ů', 'Ž', 'ž', '—', '“', '„']
number_of_chars = np.zeros((len(char_wanted)), dtype = int)
num_of_picks = 0


for pick in pickle_lst:
    num_of_picks += 1
    file = input_pckl_path + pick
    print(str(num_of_picks) + "/" + str(len(pickle_lst)) + " soubor s nazvem: " + str(pick) + " je prave zpracovavan!")
    loaded_file = pickle.load(open(file, "rb"))
    for box in loaded_file.boxes:
        for line in box.lines:
            for word in line.words:
                for char in word.characters:
                   for i in range (0,len(char_wanted)):
                       if char.character == char_wanted[i]:
                           number_of_chars[i] +=1

print(number_of_chars)
text_file = open("char_statistics.txt", "w")
text_file.write(str(number_of_chars))
text_file.close()




