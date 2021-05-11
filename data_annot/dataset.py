#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

import json
from pathlib import Path
from PIL import Image

category_num = \
    {'typewritten_heading': 1,
     'handwritten_text':    2,
     'typewritten_text':    3,
     'handwritten_heading': 4,
     'image':               5,
     'other':               6}


class AnnotatedDataset:
    """
    Annotated dataset created using CVAT and dumped into COCO format.
    """

    def __init__(self, folder : Path, annotations_file_name="instances_default.json"):
        self.folder = folder
        self.image_folder = self.folder / "images"
        self.coco_file = (self.folder / "annotations") / annotations_file_name

        if not self.coco_file.exists():
            raise FileNotFoundError(f"COCO file with annotations not found in"
                                    f"{self.coco_file}")

        with open(self.coco_file, 'r') as coco_file:
            self._coco = json.load(coco_file)

    def __iter__(self):
        for img_dict in self._coco["images"]:
            yield self._get_img_bydict(img_dict)

    def __getitem__(self, item):
        if isinstance(item, str):
            matching_imgs = list(
                filter(lambda img_dict: img_dict['file_name'] == item,
                       self._coco["images"]))
        elif isinstance(item, int):
            matching_imgs = list(filter(lambda img_dict: img_dict['id'] == item,
                                        self._coco["images"]))
        else:
            raise ValueError(f"Index item must be str or int not {item} "
                             f"of type {type(item)}.")

        if matching_imgs:
            return self._get_img_bydict(matching_imgs[0])
        else:
            IndexError(f"Image with id or name {item} not found.")

    def _get_img_bydict(self, img_dict):
        img_name = img_dict["file_name"]
        img_id = img_dict["id"]
        img_annotations = [a for a in self._coco["annotations"] if
                           a["image_id"] == img_id]
        in_img = load_img_withrotation(self.image_folder / img_name)

        return img_dict, img_annotations, in_img



def load_img_withrotation(file_path: Path):
    """
    Correctly loads i.e. rotates image file with orientation tag
    :return: PIL.Image
    """
    in_img = Image.open(str(file_path))
    exif = in_img._getexif()
    if exif is not None:
        orientation_tag = 274
        # from PIL.ExifTags.TAGS
        # [(k, v) for k, v in  PIL.ExifTags.TAGS.items() if v in ["Orientation"]
        if exif.get(orientation_tag, None) == 3:
            in_img = in_img.rotate(180, expand=True)
        elif exif.get(orientation_tag, None) == 6:
            in_img = in_img.rotate(270, expand=True)
        elif exif.get(orientation_tag, None) == 8:
            in_img = in_img.rotate(90, expand=True)
    return in_img


if __name__ == '__main__':
    d = AnnotatedDataset(Path("data_annot/task_typewritten_2"))
    for img_dict, img_annotations, img in d:
        for anot in img_annotations:
            if anot["attributes"].get("Text", "") != "":
                print(img_dict["file_name"])
                break
        pass