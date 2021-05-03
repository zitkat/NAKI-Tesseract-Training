#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from typing import List
from collections import namedtuple

from pathlib import Path
from xml.etree import ElementTree
from PIL import Image
import subprocess as sub

AnnotatedObject = namedtuple("AnnotatedObject", ["name", "text", "bndbox"])


def parse_object_tuple(object_root, shape) -> AnnotatedObject:
    """
    Parses AnnotatedObject tuple from xml object element
    """
    return AnnotatedObject(
            name=object_root.find("name").text,
            text=object_root.find("text").text.replace("\\", "")
            if object_root.find("text").text is not None else None,
            bndbox=(int(object_root.find("bndbox").find("xmin").text),
                    shape[0] - int(
                        object_root.find("bndbox").find("ymax").text),
                    int(object_root.find("bndbox").find("xmax").text),
                    shape[0] - int(object_root.find("bndbox").find("ymin").text)
                    ))


def parse_annotation_dict(annotation_root) -> dict:
    shape_root = annotation_root.find("size")
    shape = (int(shape_root.find("height").text),
             int(shape_root.find("width").text),
             int(shape_root.find("depth").text))
    objects = [parse_object_tuple(object_root, shape)
               for object_root in annotation_root.findall("object")]
    return {"shape": shape, "objects": objects}


def build_wordstrbox_lines(aobjects: List[AnnotatedObject]) -> str:
    lines = []
    for aobj in aobjects:
        if aobj.name == "image":
            continue
        xmin, ymin, xmax, ymax = aobj.bndbox
        line = f"WordStr {xmin} {ymin} {xmax} {ymax} 0 #{aobj.text} \n" \
               f"\t {xmin} {ymin} {xmax + 1} {ymax} 0\n"
        lines.append(line)
    return "".join(lines)


class NESIKUDDataset:

    def __init__(self, folder_path: Path, lang="ces"):
        self.root_dir = folder_path
        self.lang = lang
        self.image_files = list(self.root_dir.glob("*.jpg"))
        if len(self.image_files) == 0:
            print("Warning data_nesikud folder empty!")
        self.files = []
        self.annotation_files = []
        for image_pth in self.image_files:
            self.files.append(image_pth.with_suffix(""))
            annotation_pth = image_pth.with_suffix("").with_suffix(".xml")
            if not annotation_pth.exists():
                raise FileNotFoundError(
                    f"Annotation file {annotation_pth.absolute()} for"
                    f"image {image_pth.absolute()} not found.")
            self.annotation_files.append(annotation_pth)

    def __getitem__(self, idx):
        annotation_root = ElementTree.parse(
                self.annotation_files[idx]).getroot()
        annotation_dict = parse_annotation_dict(annotation_root)
        annotation_dict.update(
                {"path": self.annotation_files[idx].with_suffix("")})

        im = Image.open(self.image_files[idx])

        return annotation_dict, im

    def __len__(self):
        return len(self.image_files)

    # Tesseract conversion methods

    def get_ensured_output_folder(self, output_folder: Path = None):
        if output_folder is None:
            output_folder = self.root_dir.parent / \
                            (self.root_dir.name + "_tess")
        output_folder.mkdir(parents=True, exist_ok=True)
        return output_folder

    def _prepare_boxfiles(self,
                          output_folder: Path = None,
                          tess_annot_builder=build_wordstrbox_lines):

        output_folder = self.get_ensured_output_folder(output_folder)

        for annot, image in self:
            output_path = output_folder / annot["path"].name
            image.save(output_path.with_suffix(".jpg"))
            tess_annotations = tess_annot_builder(annot["objects"])

            with open(output_path.with_suffix(".box"), "w",
                      newline="\n",
                      encoding="utf-8") as f:
                f.write(tess_annotations)

    def _prepare_lstmf_files(self, output_folder: Path = None,
                             tesseract_path: Path = None,
                             tessdata_path: Path = None):
        """
        Creates LSTMF files for LSTM training, needs tessdata_path to access config
        files.
        :param output_folder:
        :param tesseract_path: path to tesseract executable, default just tesseract
        :param tessdata_path: default is empty, falling back to install directory
        """
        output_folder = self.get_ensured_output_folder(output_folder)

        tesseract_exec = "tesseract"
        if tesseract_path is not None:
            tesseract_exec = str(tesseract_path / tesseract_exec)

        tessdatadir_opt = ()
        if tessdata_path is not None:
            if not (tessdata_path / f"{self.lang}.traineddata").exists():
                raise FileNotFoundError(
                    f"{self.lang}.traineddata not found in tessdata folder"
                    f"{tessdata_path.absolute()}")
            if not (tessdata_path / "configs" / "lstm.train").exists():
                raise FileNotFoundError("lstm.train config files not found in",
                                        f"{(tessdata_path / 'configs').absolute()}")
            tessdatadir_opt = ("--tessdata-dir", str(tessdata_path))

        for file in self.files:
            output_path = output_folder / file.name

            tesseract_lstmf_command = (tesseract_exec,
                                       output_path.with_suffix(".jpg"),
                                       output_path.with_suffix(".box")) \
                + tessdatadir_opt + ("lstm.train",)
            print(f"===Tesseract output for file {output_path}===")
            tessout = sub.run(tesseract_lstmf_command)
            # with open(output_path.with_suffix(".tout"), "w",
            #           newline="\n",
            #           encoding="utf-8") as f:
            #     f.write(str(tessout.stdout))


    def prepare_listfile(self, output_folder: Path = None):

        output_folder = self.get_ensured_output_folder(output_folder)

        file_list = []
        for file in self.files:
            output_path = output_folder / file.name
            file_list.append(
                str(output_path.with_suffix(".box.lstmf").absolute()))

        with open(output_folder / "files_list.txt", "w",
                  newline="\n",
                  encoding="utf-8") as f:
            f.write("\n".join(file_list))

    def create_tesseract_training_files(self, output_folder: Path = None,
                                        tesseract_path: Path = None,
                                        tessdata_path: Path = None):
        self._prepare_boxfiles(output_folder)
        self._prepare_lstmf_files(output_folder, tesseract_path, tessdata_path)
        self.prepare_listfile(output_folder)
