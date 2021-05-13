#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

import random
from pathlib import Path
import ntpath
import os
import sys
import click

import albumentations as A
import codecs
import cv2
import numpy as np

import processing
from data_generation.background_generator import load_model, get_background
from utils import make_path, ensured_path, ImageText

import matplotlib.pyplot as plt

# --------------------------------------------
# DEFAULT PARAMETERS
model_dir_path = "./data/models/"
model_name = "vae_naki_wo_060218.h5"
model_path = model_dir_path + model_name

fonts_dir_path = "./data/fonts/"
fonts = [f.name for f in Path(fonts_dir_path).glob("*.ttf")]

max_dislocation_offset = 2
line_skip_denom = 2
# line_max_width = 60  # standardised
# line_max_count = 30  # standardised
foreground_color = (0, 0, 0)
# border = font_size * 4
min_contour_size = 10
# var1 = 0.3
var2 = 0.1
blur_kernel = (4, 4)
list_of_patterns = ["full", "two_columns",
                    "one_column", "two_rows",
                    "zig_zag", "title_normal"]
# parameters for calming background
high = 255  # FIXME make into parameter
gamma = 1.8
# --------------------------------------------


@click.command()
@click.argument("text_dir_path", type=Path)
@click.argument("output_dir_path", type=Path)
@click.option("-f", "--font", default="")
@click.option("-fs", "--font-size", default=45)
def main(text_dir_path, output_dir_path, font, font_size):
    """
    Synthetic files generator.
    Input: txt files
    Output: Synthetic png files + tesseract box files
    """
    output_dir_path = ensured_path(output_dir_path)
    output_box_path = make_path(output_dir_path / "annotations/", isdir=True)
    output_img_path = make_path(output_dir_path / "images/", isdir=True)

    line_skip = font_size / line_skip_denom

    run_generation(text_dir_path, font, font_size, foreground_color,
                   line_skip, model_path, max_dislocation_offset, var2,
                   min_contour_size, output_box_path, output_img_path)


def run_generation(text_dir_path, font, font_size, foreground_color,
                   line_skip, model_path, max_dislocation_offset, var2,
                   min_contour_size, output_box_path, output_img_path):
    """

    :param text_dir_path:
    :param font:
    :param font_size:
    :param foreground_color:
    :param line_skip:
    :param model_path:
    :param max_dislocation_offset:
    :param var2: variance of image gaussian noise
    :param min_contour_size:
    :param output_box_path:
    :param output_img_path:
    :return:
    """
    # Pattern type: full, two_columns, one_column, two_rows, zig_zag
    # document_pattern_type = "full"

    # LOAD TEXT FILE PATHS
    text_file_paths = []
    for ff in os.listdir(text_dir_path):
        if ff.endswith(".txt"):
            text_file_paths.append(os.path.join(text_dir_path, ff))
    if len(text_file_paths) == 0:
        sys.exit("In " + text_dir_path + " there is NO file!")
    else:
        print("Number of input text files: " + str(len(text_file_paths)))

    # LOAD VAE MODEL
    if os.path.isfile(model_path):
        vae_model = load_model(model_path)
    else:
        sys.exit("Path to the VAE model is not valid file!")
    if vae_model is None:
        sys.exit("VAE model was NOT loaded!")
    else:
        print("VAE model has been loaded!")

    # SETUP FONTS
    fix_font = bool(font)

    # CREATE TRANSFORM
    reference_images = list(map(str, Path(r"data\real").glob("*.jpg")))
    hist_transform = A.HistogramMatching(
            reference_images,
            blend_ratio=(.5, .9),
            read_fn=lambda pth: cv2.imread(pth, flags=cv2.COLOR_RGB2BGR),
            always_apply=True)

    transforms = A.Compose([
        A.RandomGamma((99, 150), p=0.75),
        A.RandomBrightnessContrast(),
        A.MedianBlur(p=.1)
    ])

    for ii, path in enumerate(text_file_paths):
        if not fix_font:
            font = fonts[ii % len(fonts)]
        font_path = fonts_dir_path + font

        print("PROCESSING ... " + path, font)

        name = os.path.splitext(ntpath.basename(path))[0]
        with codecs.open(path, "r", encoding="utf_8") as f:
            text = f.read()
            text = text.replace("\r\n", " ")

        img_background = get_background(vae_model)

        IT = ImageText((img_background.shape[1], img_background.shape[0]),
                       font_path=font_path, font_size=font_size)
        IT.write_all_text(text,
                          document_pattern_type=["full"],
                          color=foreground_color,
                          max_dislocation_offset=random.randint(1, max_dislocation_offset),
                          line_skip=line_skip)
        text_imgs = IT.convert_img_to_opencv_format()

        for idx, text_img in enumerate(text_imgs):
            # plt.figure("Text")
            # erode_txt = cv2.erode(
            #         text_img,
            #         cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4)),
            #         iterations=1
            # )
            # dilate_txt = cv2.dilate(
            #         erode_txt,
            #         cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
            #         iterations=1)
            # erode_txt = cv2.erode(
            #         dilate_txt,
            #         cv2.getStructuringElement(cv2.MORPH_RECT, (4, 5)),
            #         iterations=1
            # )
            # plt.imshow(255 - dilate_txt, cmap="Greys")
            # plt.show()
            img_background = get_background(vae_model)

            img_background = ((img_background / high) ** (1 / gamma) * 255).clip(0, 255).astype(np.uint8)
            img_combined = processing.combine_images(text_img,
                                                     img_background,
                                                     var2, blur_kernel=blur_kernel)

            pg_tuned = processing.fine_tuning_onfly(IT.page_objects[idx],
                                                    text_img,
                                                    min_contour_size)

            processing.save_page_teseract(output_box_path / (name + "_1_" + 'teseract' + ".box"),
                                          pg_tuned)

            # cv2.imwrite(str(output_img_path / (name + "_1_" + 'arig' + ".png")),
            #             img_combined)

            img_matched = hist_transform(image=img_combined)
            # cv2.imwrite(str(output_img_path / (name + "_1_" + 'mtchd' + ".png")),
            #             img_matched["image"])

            # plt.figure("Orig")
            # plt.imshow(img_combined[..., ::-1])
            img_transformed = transforms(**img_matched)
            cv2.imwrite(str(output_img_path / (name + "_1_" + 'tesseract' + ".png")),
                        img_transformed["image"])


if __name__ == '__main__':
    main()
