#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

import shutil

import click
from pathlib import Path
import subprocess as sub
from itertools import chain

from util import ensured_path


def prepare_lstmf_files(output_lstmf_path: Path,
                        lang: str = "rus",
                        tessdata_dir: Path = None,
                        tesseract_path: Path = None):
    """
    Creates LSTMF files for LSTM training, needs tessdata_path to access config
    files. output_lstmf_path must contain both images and box files.
    """
    tesseract_exec = "tesseract"
    if tesseract_path is not None:
        tesseract_exec = str(tesseract_path / tesseract_exec)

    tessdatadir_opt = ()
    if tessdata_dir is not None:
        if not (tessdata_dir / f"{lang}.traineddata").exists():
            raise FileNotFoundError(
                    f"{lang}.traineddata not found in tessdata folder"
                    f"{tessdata_dir.absolute()}")
        if not (tessdata_dir / "configs" / "lstm.train").exists():
            raise FileNotFoundError("lstm.train config file not found in",
                                    f"{(tessdata_dir / 'configs').absolute()}")
        tessdatadir_opt = ("--tessdata-dir", str(tessdata_dir))

    lstmf_files = []
    for file in chain(output_lstmf_path.glob("*.jpg"),
                      output_lstmf_path.glob("*.png"),
                      output_lstmf_path.glob("*.tif")):
        output_path = output_lstmf_path / file.name
        output_lstmf = output_path.with_suffix(".box.lstmf")

        if not output_lstmf.exists():
            tesseract_lstmf_command = (tesseract_exec,
                                       str(output_path),
                                       str(output_path.with_suffix(".box"))) \
                                      + tessdatadir_opt + ("lstm.train",)
            print(f"===Tesseract output for file {output_path}===")
            tessout = sub.run(tesseract_lstmf_command)
            if not output_lstmf.exists():
                print(f"Could not create {output_lstmf}, see tesseract log tout")
                with open(output_path.with_suffix(".tout"), "w",
                          newline="\n",
                          encoding="utf-8") as f:
                    f.write(str(tessout.stdout))
                continue
        else:
            print(f"{output_lstmf} already exists.")

        lstmf_files.append(output_path.with_suffix(".box.lstmf").absolute())

    return lstmf_files


@click.command()
@click.argument("work_folder", type=Path)
@click.option("--lang", "-l", type=str, default="rus",
              help="Lang argument for tesseract, for example eng, ces, rus, ukr")
@click.option("--tessdata-path", type=Path, help="Tessdata folder",
              default=Path("tessdata"))
def main(work_folder, lang, tessdata_path):
    """
    Process data in work_folder with images and annotations,
    copies images and box files to lstmf folder and creates lstmf files in it
    along with files_list with absolute path to each lstmf file.
    """
    input_img_path = work_folder / "images"
    input_box_path = work_folder / "annotations"
    output_lstmf_path = ensured_path(work_folder / "lstmf", isdir=True)

    for img_path in input_img_path.iterdir():
        txt_path = (input_box_path / img_path.name).with_suffix(".box")
        copy_obj(img_path, output_lstmf_path)
        copy_obj(txt_path, output_lstmf_path)

    lstmf_files = prepare_lstmf_files(output_lstmf_path, lang=lang, tessdata_dir=tessdata_path)

    open(output_lstmf_path / "files_list.txt",
         mode='w',
         newline="\n",
         encoding="utf-8",
         ).write("\n".join(map(str, output_lstmf_path.glob("*.lstmf"))))


def copy_obj(obj, output_folder):
    if not (output_folder / obj.name).exists():
        print(f"Copying {obj}")
        shutil.copy(obj, output_folder)


if __name__ == '__main__':
    main()
