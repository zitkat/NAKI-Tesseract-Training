#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from pathlib import Path
import numpy as np
from PIL import Image
import click

from data_annot.dataset import AnnotatedDataset, category_num
from util import ensured_path


@click.command()
@click.argument("dataset-path", type=Path)
@click.option("-c", "--category", multiple=True, default=["typewritten_text"],
              help="Specify categories included")
def main(dataset_path: Path, category):
    output_path = dataset_path.with_name(dataset_path.name + "_cut")
    output_path_annot = ensured_path(output_path / "annotations", isdir=True)
    output_path_images = ensured_path(output_path / "images", isdir=True)

    d = AnnotatedDataset(dataset_path)
    for img_dict, img_annotations, in_img in d:
        for anot in img_annotations:
            if anot["attributes"].get("Text", "") != "":
                if any(anot["category_id"] == category_num[cat] for cat in category):
                    cut_name = img_dict["file_name"][:-4] + "_" + str(anot["id"])

                    in_array = np.array(in_img)
                    bbox = np.array(anot["bbox"]).astype(int)
                    cut_array = in_array[bbox[1]: bbox[1] + bbox[3], bbox[0] : bbox[0] + bbox[2]]
                    cut_image = Image.fromarray(cut_array)
                    cut_image.save((output_path_images / cut_name).with_suffix(".jpg"))

                    text = anot["attributes"].get("Text", "")

                    # in case we need box file
                    # xmin = 0
                    # ymin = 0
                    # xmax = cut_array.shape[1]
                    # ymax = cut_array.shape[0]
                    # line = f"WordStr {xmin} {ymin} {xmax} {ymax} 0 #{text} \n" \
                    #        f"\t {xmin} {ymin} {xmax + 1} {ymax} 0\n"

                    open((output_path_annot / cut_name).with_suffix(".txt"),
                         mode='w',
                         encoding="utf-8",
                         ).write(text)


if __name__ == '__main__':
    main()
