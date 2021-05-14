#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from pathlib import Path
from PIL import Image
from shutil import copy
import click

from util import ensured_path


def copy_files(dest, box_file_path, image_file_path, text_file_path,
               output_images_paths, output_texts_paths):
    copy(text_file_path, output_texts_paths[dest])
    copy(image_file_path, output_images_paths[dest])
    if box_file_path.exists():
         copy(box_file_path, output_texts_paths[dest])


@click.command()
@click.argument("dataset-path", type=Path)
@click.option("-o", "--output_path", default=None)
@click.option("-tr", "--text-ratio", type=float, default=6.0)
@click.option("-ml", "--max-length", type=int, default=10,
              help="Maximal length of text to automatically consider single line")
def main(dataset_path, output_path, text_ratio, max_length):
    input_images = dataset_path / "images"
    input_texts = dataset_path / "annotations"

    if not output_path:
        output_path = dataset_path.parent / (dataset_path.name + "_filtered")
    output_path = ensured_path(output_path, isdir=True)

    output_images_paths = {i: ensured_path(output_path / str(i) / "images", isdir=True)
                           for i in (1, "more")}
    output_texts_paths = {i: ensured_path(output_path / str(i) / "annotations", isdir=True)
                          for i in (1, "more")}

    for text_file_path in input_texts.glob("*.txt"):

        file_name = text_file_path.name
        image_file_path : Path = (input_images / file_name).with_suffix(".jpg")
        box_file_path : Path= (input_texts / file_name).with_suffix(".box")

        text = open(text_file_path, 'r', encoding='utf-8').read()
        heur_coef = len(text)/text_ratio
        if len(text) > max_length:
            image_file = Image.open(image_file_path)
            if heur_coef*image_file.size[1] > image_file.size[0]:
                print(f"more: { text_file_path }")
                copy_files("more", box_file_path, image_file_path, text_file_path,
                           output_images_paths, output_texts_paths)
            else:
                print(f"1: { text_file_path }")
                copy_files(1, box_file_path, image_file_path,
                           text_file_path,
                           output_images_paths, output_texts_paths)
        else:
            print(f"1: {text_file_path}")
            copy_files(1, box_file_path, image_file_path,
                       text_file_path,
                       output_images_paths, output_texts_paths)


if __name__ == '__main__':
    main()