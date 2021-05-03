#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Text statistics calculation.
"""

import _pickle as pickle
import os.path
import numpy as np
import matplotlib.pyplot as plt

input_pg_path = "//147.228.125.178/home/Generated_texts/noisy_04_NEW/pg_pickle/"
pickle_lst = os.listdir(input_pg_path)
pickle_lst.sort()
avg_h = 0
variance_h = 0
avg_w = 0
variance_w = 0
avg_wrds = 0
variance_wrds = 0
num_of_wrds = 0
num_of_lines = 0
num_of_picks = 0
x = np.arange(3000)
hist = np.zeros(3000)
max_lines = 0

for pick in pickle_lst:
    if pick[-11:-7] == 'full':
        file = input_pg_path + pick
        num_of_picks +=1
        print(str(num_of_picks)+"/"+str(len(pickle_lst))+" soubor s nazvem: "+str(pick)+" je prave zpracovavan!")
        loaded_file = pickle.load( open(file, "rb"))
        boxes = loaded_file.boxes
        for i in range(0,len(boxes)):
            lines = boxes[i].lines
            if max_lines<len(lines):
                max_lines = len(lines)
            for j in range(0,len(lines)):
                words = lines[j].words
                num_of_lines +=1
                variance_wrds = (num_of_lines*(variance_wrds + avg_wrds**2)+len(words)**2)/(num_of_lines+1) - (((num_of_lines-1)*avg_wrds + len(words))/num_of_lines)**2
                avg_wrds = ((num_of_lines-1)*avg_wrds + len(words))/num_of_lines
                for k in range(0,len(words)):
                    word = words[k]
                    num_of_wrds +=1
                    variance_h = (num_of_wrds*(variance_h + avg_h**2)+word.h**2)/(num_of_wrds+1) - (((num_of_wrds-1)*avg_h + word.h)/num_of_wrds)**2
                    avg_h = ((num_of_wrds-1)*avg_h + word.h)/num_of_wrds
                    variance_w = (num_of_wrds*(variance_w + avg_w**2)+word.w**2)/(num_of_wrds+1) - (((num_of_wrds-1)*avg_w + word.w)/num_of_wrds)**2
                    avg_w = ((num_of_wrds-1)*avg_w + word.w)/num_of_wrds
                    hist[word.w] = hist[word.w]+1

text_file = open("statistics_out_04_NEW2.txt", "w") #output text file
text_file.write("Total number of words is: "+str(num_of_wrds)+"\n")
text_file.write("Average number of words per line is: "+str(avg_wrds)+"\n")
text_file.write("Standard deviation of number of words per line is: "+str(np.sqrt(variance_wrds))+"\n")
text_file.write("Average height is: "+str(avg_h)+"\n")
text_file.write("Standard deviation of height is: "+str(np.sqrt(variance_h))+"\n")
text_file.write("Average width is: "+str(avg_w)+"\n")
text_file.write("Standard deviation of width is: "+str(np.sqrt(variance_w))+"\n")
text_file.write("Maximum number of lines is: "+str(max_lines)+"\n")
text_file.close()

print("---------------------------------------")
print("Total number of words is: "+str(num_of_wrds))
print("Average number of words per line is: "+str(avg_wrds))
print("Standard deviation of number of words per line is: "+str(np.sqrt(variance_wrds)))
print("Average height is: "+str(avg_h))
print("Standard deviation of height is: "+str(np.sqrt(variance_h)))
print("Average width is: "+str(avg_w))
print("Standard deviation of width is: "+str(np.sqrt(variance_w)))
print("Maximum number of lines is: "+str(max_lines)+"\n")

plt.plot(x, hist)
plt.show()