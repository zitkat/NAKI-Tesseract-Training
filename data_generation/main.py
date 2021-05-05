#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Synthetic files generator.
Input: txt files
Output: Synthetic png files + json files with annotations
"""

import ntpath
import os
import sys
from background_generator import *
import cv2
import codecs
from PIL import ImageFont
import utils
import processing

# ----------------------------------------------------------------------------------------------------------------------
# SET PARAMETERS
text_dir_path = "./data/texts_all/"
model_dir_path = "./data/models/"
model_name = "vae_naki_wo_060218.h5"
model_path = model_dir_path + model_name

# output_dir_path = "./data/outputs/"
output_dir_path = "./data/teseract/"
output_pg_path = output_dir_path + "pg_pickle/"
output_box_path = output_dir_path + "annotations/"
output_img_path = output_dir_path + "images/"

fonts_dir_path = "./data/fonts/"
font_path = fonts_dir_path + "LITERPLA.ttf"
font_size = 45
line_skip = font_size / 2
font = ImageFont.truetype(font_path, font_size)
font_title = ImageFont.truetype(font_path, 4*font_size)

max_dislocation_offset = 1
line_max_width = 60  # standardised
line_max_count = 30  # standardised
foreground_color = (0, 0, 0)
border = font_size * 4
min_contour_size = 10
# var1 = 0.3
var2 = 0.4

# Pattern type: full, two_columns, one_column, two_rows, zig_zag
#document_pattern_type = "full"
list_of_patterns = ["full", "two_columns", "one_column", "two_rows", "zig_zag", "title_normal"]
# ----------------------------------------------------------------------------------------------------------------------
# LOAD TEXT FILE PATHS
text_file_paths = []
for ff in os.listdir(text_dir_path):
    if ff.endswith(".txt"):
        text_file_paths.append(os.path.join(text_dir_path, ff))

if len(text_file_paths) == 0:
    sys.exit("In " + text_dir_path + " there is NO file!")
else:
    print("Number of input text files: " + str(len(text_file_paths)))


# ----------------------------------------------------------------------------------------------------------------------
# LOAD VAE MODEL
if os.path.isfile(model_path):
    vae_model = load_model(model_path)
else:
    sys.exit("Path to the VAE model is not valid file!")

if vae_model is None:
    sys.exit("VAE model was NOT loaded!")
else:
    print("VAE model has been loaded!")


# ----------------------------------------------------------------------------------------------------------------------
# PROCESS
for path in text_file_paths:
    name = os.path.splitext(ntpath.basename(path))[0]
    with codecs.open(path, "r", encoding="utf_8") as f:
        text = f.read()
        text = text.replace("\r\n", " ")

        img_background = get_background(vae_model)
        # create object for image text processing
        IT = utils.ImageText((img_background.shape[1], img_background.shape[0]),
                             font_path=font_path, font_size=font_size)

        # write all text into white/empty image
        print("PROCESSING ... " + path)
        IT.write_all_text(text, document_pattern_type=["full"],  color=foreground_color,
                          max_dislocation_offset=max_dislocation_offset, line_skip=line_skip)
        text_imgs = IT.convert_img_to_opencv_format()

        for idx, text_img in enumerate(text_imgs):
            img_background = get_background(vae_model)
            img_combined = processing.combine_images(text_img, img_background, var2)
            pg_tuned = processing.fine_tuning_onfly(IT.page_objects[idx], text_img, min_contour_size)
            processing.save_page_teseract(output_box_path + name + "_1_" + 'teseract' + ".box", pg_tuned)
            # processing.save_page(output_pg_path + name + "_4_" + ".pickle", pg_tuned)
            cv2.imwrite(output_img_path + name + "_1_" + 'teseract' +".png", img_combined)

            # IT.visualize(output_img_path + name + "_1_" + 'teseract' +".png", output_pg_path + name + "_4_" + ".pickle", output_img_path + name + "result_TFF_lines.png",
            #          draw_lines=True, draw_words=True, draw_characters=True, visualize=False)

    # ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
