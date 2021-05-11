#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from pathlib import Path
import argparse
import sys
import click


@click.command(epilog='(c) 2020 T. Zitka, KKY UWB')
@click.option("-d", "--dataset_path",
              type=Path,
              default=Path("data_nesikud/nesikud_data"),
              help="Path to root directory with images and annotations")
@click.option("-t", "--tesseract_path",
              type=Path,
              default=None,
              help="Path to directory with tesseract executable, if empty "
                   "relies on tesseract being on PATH.")
@click.option("-td", "--tessdata_path",
              type=Path,
              default=Path("tessdata"),
              help="Path to tessdata directory if empty "
                   "relies on tessdata in tesseract instalation.")
@click.option("-m", "--model_name",
              type=str,
              default="ces",
              help="Model name in ***.traineddata")
@click.option("-o", "--output_path",
              type=Path,
              default=Path("output"),
              help="Where to put tesseract training files, "
                   "if empty appends 'tess' to data_nesikud path")
def main(dataset_path, tesseract_path, tessdata_path, model_name, output_path):
    """
    Script for running tesseract on images in folder dataset_path,
    outputs hocr.
    """

    tesseract_exec = "tesseract"
    if tesseract_path is not None:
        tesseract_exec = str(tesseract_path / tesseract_exec)

    for imagepath in dataset_path.glob("*.jpg"):
        command = [tesseract_exec, imagepath.absolute(),
                   (output_path / imagepath.name).with_suffix("").absolute()]
        command += ["--tessdata-dir", tessdata_path.absolute()]
        command += ["-l", model_name]
        command += ["hocr"]  # TODO make into option

        # sub.run(command)
        hocr_path = (output_path / imagepath.name).with_suffix(".hocr").absolute()
        html_path = (output_path / imagepath.name).with_suffix(".html").absolute()
        with open(hocr_path, "r", encoding="utf-8") as hocr:
            with open(html_path, "w", encoding="utf-8") as html:
                for line in hocr:
                    if "</body>" in line:
                        html.write('<script src="https://unpkg.com/hocrjs"></script>')
                    html.write(line)





if __name__ == '__main__':
    main(None)
