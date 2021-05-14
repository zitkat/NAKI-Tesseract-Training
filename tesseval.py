#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"

from typing import List
from collections import namedtuple

import click
import pandas as pd
from pathlib import Path
from PIL import Image


from tesserocr import PyTessBaseAPI, PSM, OEM, RIL, iterate_level
from Levenshtein import distance
import fastwer


from util import ensured_path

TesseractResult = namedtuple("TesseractResult", "blockType, x0, y0, x1, y1, score, word")


def getBlockType(blockNumber):
    namesOfBlocks = ["Unknown", "FlowingText", "HeadingText", "PullOutText", "Equation", "InlineEquation", "Table",
                     "VerticalText", "CaptionText", "FlowingImage", "HeadingImage", "PullOutImage", "HorizontalLine",
                     "VerticalLine", "Noise", "Count"]
    blockType = namesOfBlocks[blockNumber]
    return blockType


def getSimpleBlockType(blockNumber):
    namesOfBlocks = ["image", "paragraph", "title", "paragraph", "title", "title", "paragraph",
                     "paragraph", "caption", "image", "image", "image", "image",
                     "image", "image", "image"]
    blockType = namesOfBlocks[blockNumber]
    return blockType


def text_from_results(results: List[TesseractResult]) -> str:
    words = [i.word for i in results]
    text = " ".join(words)
    return text


def tesseract(api, image) -> List[TesseractResult]:
    """
    Runs tesseract inference in provided api.
    """
    api.SetVariable("user_defined_dpi", "300")
    api.SetImage(image)
    api.Recognize()
    results = []
    iterator = api.GetIterator()
    level = RIL.BLOCK
    if not iterator.Empty(level):
        for e in iterate_level(iterator, level):
            word = e.GetUTF8Text(level)
            conf = e.Confidence(level) / 100.
            x0, y0, x1, y1 = e.BoundingBox(level)
            block_type = getSimpleBlockType(e.BlockType())
            results.append(
                    TesseractResult(block_type, x0, y0, x1, y1, conf, word))
    if results:
        avg_conf = sum(i.score for i in results) / len(results)
    else:
        avg_conf = 0.
    return results


@click.command(epilog='(c) 2021 T. Zitka, KKY UWB')
@click.option("-d", "--dataset-path",
                    type=Path,
                    default=Path(r"D:\Datasets\NAKI\annotated\task_typewritten_2_cut"),
                    help="Path to root directory with images and annotations in corresponding folders.")
@click.option("-td", "--tessdata-path",
                     type=Path,
                     default=Path("tessdata"),
                     help="Path to tessdata directory")
@click.option("-m", "--model-name",
                    type=str,
                    default="rus",
                    help="Model name in ***.traineddata")
@click.option("-o", "--output-path",
                    type=Path,
                    default=Path("output"),
                    help="Where to put tesseract training files, "
                         "if empty appends 'tess' to data_nesikud path")
def main(dataset_path: Path,  tessdata_path: Path, model_name: str, output_path: Path):
    """
    This script evaulates model, which has to be present in <tessdata> directory
    as <model_name>.traineddata on dataset in <dataset-path>. The dataset must be
    composed of *.jpg images and *.txt annotations. Output is a csv files with
    Levenstein distance, CER and WER for each image. Newlines are ignored.
    """
    input_imgs_path = dataset_path / "images"
    input_txts_path = dataset_path / "annotations"


    data_list = []
    with PyTessBaseAPI(path=str(tessdata_path.absolute()).replace('\\', "/") + r"/.",
                       lang=model_name,
                       psm=PSM.AUTO, oem=OEM.LSTM_ONLY) as api:
        for imagepath, truth_path in zip(input_imgs_path.glob("*.jpg"),
                                         input_txts_path.glob("*.txt")):
            image = Image.open(imagepath)
            truth_text = open(truth_path, encoding="utf-8").read().replace("\n", "")

            results = tesseract(api, image)
            ocr_text = " ".join(text_from_results(results).split())

            print("Tru:", truth_text)
            print("OCR:", ocr_text)

            data_list.append(dict(name=imagepath.name,
                                  tlen=len(truth_text),
                                  olen=len(ocr_text),
                                  lev=distance(truth_text, ocr_text),
                                  wer=fastwer.score_sent(truth_text, ocr_text),
                                  cer=fastwer.score_sent(truth_text, ocr_text,
                                                         char_level=True)
                                  ))
            print(data_list[-1])

    df = pd.DataFrame(data_list)
    df.to_csv(ensured_path(output_path / (model_name + "_annot_eval.csv")))


if __name__ == '__main__':
    main()
