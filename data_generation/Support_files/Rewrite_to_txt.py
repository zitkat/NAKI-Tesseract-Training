#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Text rewrite from pickle to txt without spaces and lines
"""


#Prepis textu z picklu do txt, bez mezer a radek

import _pickle as pickle
import os.path
import codecs

input_dir_path = "//147.228.125.178/home/Generated_texts/noisy_04_NEW/"

input_pckl_path = input_dir_path + "pg_pickle/"

pickle_lst = os.listdir(input_pckl_path)

pickle_lst.sort()

for i in range (500,600):
    file = input_pckl_path + ''.join(pickle_lst[i:i + 1])
    loaded_pickle = pickle.load(open(file, "rb"))
    output_txt = 'E:/FileGenerator/rewrite_txt/text_'+str(i-500)+'.txt'
    with codecs.open(output_txt, 'w', encoding='utf8') as file:
        print('Zapis do souboru ' +output_txt+' zahajen!')
        for box in loaded_pickle.boxes:
            for line in box.lines:
                for word in line.words:
                    for char in  word.characters:
                        file.write(char.character)
    file.close()
    print('Zapis dokoncen!')

print('Hotovo!')