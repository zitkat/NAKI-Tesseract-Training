#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from pathlib import Path
import argparse
import sys

from data_nesikud.nesikud_dataset import NESIKUDDataset


def main(argv):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Script for loading and converting NESIKUD data_nesikud '
                    'to Tesseract training data.',
        epilog='(c) 2020 T. Zitka, KKY UWB')
    parser.add_argument("-d", "--dataset_path",
                        type=Path,
                        help="Path to root directory with images and annotations")
    parser.add_argument("-t", "--tesseract_path",
                        type=Path,
                        help="Path to directory with tesseract executable, if empty "
                             "relies on tesseract being on PATH.")
    parser.add_argument("-td", "--tessdata_path",
                        type=Path,
                        help="Path to tessdata directory if empty "
                             "relies on tessdata in tesseract instalation.")
    parser.add_argument("-o", "--output_path",
                        type=Path,
                        default=None,
                        help="Where to put tesseract training files, "
                             "if empty appends 'tess' to data_nesikud path")


    opt, unknown = parser.parse_known_args(argv)



    nd = NESIKUDDataset(opt.dataset_path)
    nd.create_tesseract_training_files(opt.output_path,
                                       opt.tesseract_path,
                                       opt.tessdata_path)


if __name__ == '__main__':
    main(None)
