#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from pathlib import Path

import click

from data_nesikud.nesikud_dataset import NESIKUDDataset


@click.command(
    epilog='(c) 2020 T. Zitka, KKY UWB')
@click.option("-d", "--dataset_path",
                    type=Path,
                    help="Path to root directory with images and annotations")
@click.option("-t", "--tesseract_path",
                    type=Path,
                    help="Path to directory with tesseract executable, if empty "
                         "relies on tesseract being on PATH.")
@click.option("-td", "--tessdata_path",
                    type=Path,
                    help="Path to tessdata directory if empty "
                         "relies on tessdata in tesseract instalation.")
@click.option("-o", "--output_path",
                    type=Path,
                    default=None,
                    help="Where to put tesseract training files, "
                         "if empty appends 'tess' to data_nesikud path")
def main(dataset_path, tesseract_path, tessdata_path, output_path):
    """
    Script for loading and converting NESIKUD
    to Tesseract training data.
    """

    nd = NESIKUDDataset(dataset_path)
    nd.create_tesseract_training_files(output_path,
                                       tesseract_path,
                                       tessdata_path)


if __name__ == '__main__':
    main()
