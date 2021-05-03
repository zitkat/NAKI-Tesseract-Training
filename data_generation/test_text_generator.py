#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

from PIL import Image
import os
import codecs
import cv2
import processing
import utils


def check_line(count, max_count):
    if count > max_count:
        print ("Too many lines ... maximum is: " + str(max_count))
        exit(1)


# ----------------------------------------------------------------------------------------------------------------------
# LOAD DATA
print("OpenCV version: " + cv2.__version__ + "\n")

fname = "./data/texts/test.txt"
with codecs.open(fname, "r", encoding="utf8") as f:
    text = f.read()

prefix_path = "./data/background_images/"
all_files = os.listdir(prefix_path)
background_file_paths = []
for f in all_files:
    if "png" in f:
        # print "Loading: " + f
        background_file_paths.append(prefix_path + f)

# ----------------------------------------------------------------------------------------------------------------------
# SET PARAMETERS
background_file_path = background_file_paths[5]
font_size = 64
max_dislocation_offset = 3
line_max_width = 60  # standardised
line_max_count = 30  # standardised
foreground_color = (0, 0, 0)
# font = ImageFont.truetype("./data/fonts/Bohemian typewriter.ttf", font_size)
# lines = textwrap.wrap(text, width=line_max_width)
dst_path = "./data/out/"
img_text_name = "text.png"
bboxes_name = "bboxes.dat"
border = font_size * 2
min_contour_size = 10

# ----------------------------------------------------------------------------------------------------------------------
# CHECKS
# check_line(len(lines), line_max_count)

# ----------------------------------------------------------------------------------------------------------------------
# PROCESSING
print("PROCESSING ...",)
IT = utils.ImageText(Image.open(background_file_path).size)
IT.write_text_box((5 * border, 5 * border), text, 5 * border, 5 * border, "./data/fonts/Bohemian typewriter.ttf", font_size=font_size)
IT.save_images(dst_path, img_text_name)
IT.save_pages(dst_path, "page_obj.pickle")

img_background = cv2.imread(background_file_path, 1)
img_text = cv2.imread(dst_path + img_text_name, 0)
img_combined = processing.combine_images(img_text, img_background)
cv2.imwrite(dst_path + "combined.png", img_combined)
print("DONE!\n")

# ----------------------------------------------------------------------------------------------------------------------
# FINE-TUNING
print("FINE-TUNING ...",)
processing.fine_tuning(dst_path, "page_obj.pickle", dst_path + img_text_name, min_contour_size)
print("DONE!\n")

# ----------------------------------------------------------------------------------------------------------------------
# TESTING
print("TESTING ...",)
IU = utils.ImageText()
IU.visualize(dst_path + img_text_name, dst_path + "page_obj.pickle", dst_path + "result_TFF_lines.png",
             draw_lines=True, draw_words=False, draw_characters=False, visualize=False)
IU.visualize(dst_path + img_text_name, dst_path + "page_obj.pickle", dst_path + "result_FTF_words.png",
             draw_lines=False, draw_words=True, draw_characters=False, visualize=False)
IU.visualize(dst_path + img_text_name, dst_path + "page_obj.pickle", dst_path + "result_FFT_characters.png",
             draw_lines=False, draw_words=False, draw_characters=True, visualize=False)

IU.visualize(dst_path + img_text_name, dst_path + "page_obj_tuned.pickle", dst_path + "result_tuned_TFF_lines.png",
             draw_lines=True, draw_words=False, draw_characters=False, visualize=False)
IU.visualize(dst_path + img_text_name, dst_path + "page_obj_tuned.pickle", dst_path + "result_tuned_FTF_words.png",
             draw_lines=False, draw_words=True, draw_characters=False, visualize=False)
IU.visualize(dst_path + img_text_name, dst_path + "page_obj_tuned.pickle", dst_path + "result_tuned_FFT_characters.png",
             draw_lines=False, draw_words=False, draw_characters=True, visualize=False)
print("DONE!\n")

print("PRINTING ... \n")
pg = IU.load_page(dst_path + "page_obj_tuned.pickle")
print("Total sentences on page is: " + str(pg.get_total_sentences()) + "\n")
pg.print_all_sentences()
print("\n" + pg.get_text())
