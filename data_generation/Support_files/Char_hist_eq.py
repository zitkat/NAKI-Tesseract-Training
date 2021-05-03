#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "0.0.1"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Character weights calculation
!!!!!There is probably mistake in it!!!!!
"""

import numpy as np
import matplotlib.pyplot as plt
import h5py

f = open("char_statistics.txt", "r")
lines = f.read().split(' ')
oprava = lines[len(lines)-1]
oprava = oprava[:-1]
lines[len(lines)-1] = oprava
cislo_radku = 0
uspech = 0
char_wanted = ['!', '"', '&', "'", '(', ')', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '=', '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z', '[', ']', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '|', '§', 'Á', 'É', 'Í', 'Ú', 'Ý', 'á', 'é', 'í', 'ó', 'ú', 'ý', 'Č', 'č', 'ď', 'Ě', 'ě', 'ň', 'Ř', 'ř', 'Š', 'š', 'ť', 'ů', 'Ž', 'ž', '—', '“', '„']
number_of_chars = np.zeros((len(char_wanted)), dtype = int)
for l in lines:
    try:
        l_num = int(l)
        print("Radek cislo: "+str(cislo_radku)+" s hodnotou: "+ str(l_num)+" bylo uspesne prevedeno!")
        cislo_radku +=1
        number_of_chars[uspech] = l_num
        uspech += 1
    except ValueError:
        print("Radek cislo: "+str(cislo_radku)+" s hodnotou: "+ l +" se nepodarilo prevest!")
        cislo_radku +=1
# print("Pocet uspechu: " + str(uspech))
# print("Hotovo!")
f.close()
print(number_of_chars)
plt.plot(number_of_chars)
threshold = int(0.6*np.max(number_of_chars))
rozdil = 0
while True:
    for i in range (0,len(char_wanted)):
        if number_of_chars[i]>threshold:
            rozdil += number_of_chars[i]-threshold
            number_of_chars[i] = threshold
    number_of_chars +=int(rozdil/len(char_wanted))
    rozdil = 0
    if np.max(number_of_chars)<=threshold:
        break

print(number_of_chars)
plt.plot(number_of_chars)
plt.show()
number_of_chars = number_of_chars/sum(number_of_chars)
# text_file = open("char_hist_eq.txt", "w")
# text_file.write(str(number_of_chars))
# text_file.close()

f_out = h5py.File("weights.h5", 'w')
data = f_out.create_dataset('data', shape=(1, len(char_wanted)), maxshape=(1, len(char_wanted)), dtype=np.float32)
data[0,:] = number_of_chars
f_out.close()
print('Hotovo!')


