#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from pathlib import Path
import argparse
import sys
import subprocess as sub


def main(argv):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Script for running tesseract on given data_nesikud',
        epilog='(c) 2020 T. Zitka, KKY UWB')
    parser.add_argument("-d", "--dataset_path",
                        type=Path,
                        default=Path("data_nesikud/nesikud_data"),
                        help="Path to root directory with images and annotations")
    parser.add_argument("-t", "--tesseract_path",
                        type=Path,
                        default=None,
                        help="Path to directory with tesseract executable, if empty "
                             "relies on tesseract being on PATH.")
    parser.add_argument("-td", "--tessdata_path",
                        type=Path,
                        default=Path("tessdata"),
                        help="Path to tessdata directory if empty "
                             "relies on tessdata in tesseract instalation.")
    parser.add_argument("-m", "--model_name",
                        type=str,
                        default="ces",
                        help="Model name in ***.traineddata")
    parser.add_argument("-o", "--output_path",
                        type=Path,
                        default=Path("output"),
                        help="Where to put tesseract training files, "
                             "if empty appends 'tess' to data_nesikud path")


    opt, unknown = parser.parse_known_args(argv)

    tesseract_exec = "tesseract"
    if opt.tesseract_path is not None:
        tesseract_exec = str(opt.tesseract_path / tesseract_exec)

    for imagepath in opt.dataset_path.glob("*.jpg"):
        command = [tesseract_exec, imagepath.absolute(),
                   (opt.output_path / imagepath.name).with_suffix("").absolute()]
        command += ["--tessdata-dir", opt.tessdata_path.absolute()]
        command += ["-l", opt.model_name]
        command += ["hocr"]

        # sub.run(command)
        hocr_path = (opt.output_path / imagepath.name).with_suffix(".hocr").absolute()
        html_path = (opt.output_path / imagepath.name).with_suffix(".html").absolute()
        with open(hocr_path, "r", encoding="utf-8") as hocr:
            with open(html_path, "w", encoding="utf-8") as html:
                for line in hocr:
                    if "</body>" in line:
                        html.write('<script src="https://unpkg.com/hocrjs"></script>')
                    html.write(line)





if __name__ == '__main__':
    main(None)
