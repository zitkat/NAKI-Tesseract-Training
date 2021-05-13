#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import _pickle as cPickle
import objects
import cv2
from random import randint
import numpy as np
from page_patterns import Pattern
from pathlib import Path


def make_path(*pathargs, isdir=False, **pathkwargs):
    new_path = Path(*pathargs, **pathkwargs)
    return ensured_path(new_path, isdir=isdir)


def ensured_path(path: Path, isdir=False):
    if isdir:
        path.mkdir(parents=True, exist_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path

class ImageText(object):
    def __init__(self, filename_or_size=None, font_path=None, font_size=0,
                 mode="RGB", background=(255, 255, 255), encoding="utf_8"):
        self.mode = mode
        self.background = background
        self.encoding = encoding  # unused
        self.font_path = font_path
        self.font_size = font_size
        self.font = [ImageFont.truetype(self.font_path, self.font_size),
                     ImageFont.truetype(self.font_path, 4 * self.font_size)]

        if isinstance(filename_or_size, str):
            self.filename = filename_or_size
            image = Image.open(self.filename)
            self.size = image.size
        elif isinstance(filename_or_size, (list, tuple)):
            self.filename = None
            self.size = filename_or_size
            image = Image.new(self.mode, self.size, color=self.background)
        else:
            self.filename = None
            image = None
            self.size = None

        self.images = []
        self.page_objects = []
        self.page_objects.append(objects.Page())
        self.images.append(image)
        self.draw = ImageDraw.Draw(self.images[0])

    def add_page(self):
        page = objects.Page()
        self.page_objects.append(page)

    def add_image(self):
        image = Image.new(self.mode, self.size, color=self.background)
        self.images.append(image)

    def set_draw_image(self):
        self.draw = ImageDraw.Draw(self.images[-1])

    def convert_img_to_opencv_format(self):
        converted = []
        for img in self.images:
            converted.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY))
        return converted

    def save_images(self, image_path, image_filename):
        for i, f in enumerate(self.images):
            path = image_path + str(i) + "_" + image_filename
            f.save(path)

    def save_pages(self, page_path, page_filename):
        for i, pg in enumerate(self.page_objects):
            path = page_path + str(i) + "_" + page_filename
            with open(path, 'wb') as pickle_file:
                cPickle.dump(pg, pickle_file)

    @staticmethod
    def load_page(page_filename):
        with open(page_filename, 'rb') as pickle_file:
            pg = cPickle.load(pickle_file)
        return pg

    # def get_font_size(self, text, font, max_width=None, max_height=None):
    #     if max_width is None and max_height is None:
    #         raise ValueError('You need to pass max_width or max_height')
    #     font_size = 1
    #     text_size = self.get_text_size(font, font_size, text)
    #     if (max_width is not None and text_size[0] > max_width) or (max_height is not None and text_size[1] > max_height):
    #         raise ValueError("Text can't be filled in only (%dpx, %dpx)" % text_size)
    #     while True:
    #         if (max_width is not None and text_size[0] >= max_width) or (max_height is not None and text_size[1] >= max_height):
    #             return font_size - 1
    #         font_size += 1
    #         text_size = self.get_text_size(font, font_size, text)

    def get_font_size(self, text, font, max_width=None, max_height=None):
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        font_size = 1
        text_size = self.get_text_size(text)
        if (max_width is not None and text_size[0] > max_width) or (
                max_height is not None and text_size[1] > max_height):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" % text_size)
        while True:
            if (max_width is not None and text_size[0] >= max_width) or (
                    max_height is not None and text_size[1] >= max_height):
                return font_size - 1
            font_size += 1
            text_size = self.get_text_size(text)

    # def write_text(self, x_y, text, font_filename, font_size=11, color=(0, 0, 0), max_width=None, max_height=None):
    #     x, y = x_y
    #     #if isinstance(text, str):
    #     #    text = text.decode(self.encoding)
    #
    #     if font_size == 'fill' and (max_width is not None or max_height is not None):
    #         font_size = self.get_font_size(text, font_filename, max_width, max_height)
    #
    #     text_size = self.get_text_size(font_filename, font_size, text)
    #     font = ImageFont.truetype(font_filename, font_size)
    #     if x == 'center':
    #         x = (self.size[0] - text_size[0]) / 2
    #     if y == 'center':
    #         y = (self.size[1] - text_size[1]) / 2
    #     self.draw.text((x, y), text, font=font, fill=color)
    #     return text_size

    def write_text(self, x_y, text, color, font):
        x, y = x_y
        text_size = self.get_text_size(text)
        # text_to_write = "\u0332".join(text)
        # self.draw.text((x, y), text_to_write, font=font, fill=color)
        self.draw.text((x, y), text, font=font, fill=color)
        return text_size

    def write_text_to_empty_img(self, x_y, text, color, font):
        x, y = x_y
        image = Image.new("RGB", (font.size * 2, font.size * 2), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((x, y), text, font=font, fill=color)
        return image

    def get_text_size(self, text):
        return self.font[0].getsize(text)

    # @staticmethod
    # def get_text_size(font_filename, font_size, text):
    #     font = ImageFont.truetype(font_filename, font_size)
    #     return font.getsize(text)

    @staticmethod
    def get_dislocations(max_dislocation_offset=2):
        max_rand = 2 * max_dislocation_offset
        offset_x = randint(0, max_rand) - max_dislocation_offset
        offset_y = randint(0, max_rand) - max_dislocation_offset
        return offset_x, offset_y

    def get_lines_for_box(self, box, text):
        lines = []
        line = []
        paragraphs = text.splitlines()
        for idx, par in enumerate(paragraphs):
            if par == "":
                lines.append("\n")
            else:
                words = par.split()
                for word in words:
                    new_line = ' '.join(line + [word])
                    size = self.get_text_size(new_line)
                    if size[0] <= box.w:
                        line.append(word)
                    else:
                        lines.append(line)
                        line = [word]
                if line:
                    lines.append(line)
                    line = []
        lines = [' '.join(line) for line in lines if line]
        return lines

    def lines_reformat(self, box, lines, used_lines):
        text = ""
        first = True
        for idx, line in enumerate(lines):
            if idx > used_lines:
                if line == "\n":
                    text += "\n\n"
                else:
                    if first:
                        text += line
                        first = False
                    else:
                        text += " " + line

        return self.get_lines_for_box(box, text)

    def get_pixels(self, img, offset_x, offset_y):
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        # _, thresh_img = cv2.threshold(cv_img, 0, 255, cv2.THRESH_BINARY_INV)
        thresh_img = (cv_img < 255)
        yx_coordinates = np.argwhere(thresh_img == 1)
        yx_coordinates = np.array(yx_coordinates)

        yx_coordinates[:, 0] = yx_coordinates[:, 0] + offset_y
        yx_coordinates[:, 1] = yx_coordinates[:, 1] + offset_x

        # cv2.imshow("",thresh_img)
        # cv2.waitKey(0)
        return yx_coordinates

    def write_all_text(self, text, document_pattern_type=[], color=(0, 0, 0),
                       max_dislocation_offset=2, line_skip=0):
        # 1 page object exist
        self.page_objects[-1].resolution_w = self.size[0]
        self.page_objects[-1].resolution_h = self.size[1]
        self.page_objects[-1].pattern_type = document_pattern_type

        # get pattern boxes
        pattern = Pattern(self.font, document_pattern_type,
                          self.font_size, self.size[0], self.size[1])
        pattern_boxes = pattern.process()

        # size = self.get_text_size("A")
        # text_height = size[1]

        _used_lines = 0

        for box_idx, pattern_box in enumerate(pattern_boxes):
            size = pattern_box.get_text_size("A")
            text_height = size[1]
            obj_box = objects.Box()
            x = pattern_box.x
            # yy = pattern_box.y - pattern_box.font_size
            yy = pattern_box.y

            if box_idx == 0:
                lines = self.get_lines_for_box(pattern_box, text)
            else:
                lines = self.lines_reformat(pattern_box, lines, _used_lines)

            breaked = False
            for line_idx, line in enumerate(lines):
                yy += text_height  + line_skip
                xx = x

                # Check new page,
                if yy >= (pattern_box.y + pattern_box.h - text_height):
                    breaked = True
                    break

                # new line
                if line == "\n":
                    continue

                obj_box.add_line(objects.Line())
                words = line.split()
                for word_idx, word in enumerate(words):
                    obj_word = objects.Word()
                    for char in word:
                        offset_x, offset_y = self.get_dislocations(max_dislocation_offset)
                        self.write_text((xx + offset_x, yy + offset_y), char, color, pattern_box.font)
                        ch_w, ch_h = pattern_box.get_text_size(char)


                        blank_img_with_char_offset = 10
                        blank_img_with_char = self.write_text_to_empty_img(
                            (blank_img_with_char_offset, blank_img_with_char_offset),
                            char, color, font=pattern_box.font)
                        cropped = blank_img_with_char.crop((blank_img_with_char_offset, blank_img_with_char_offset,
                                                            blank_img_with_char_offset + ch_w,
                                                             blank_img_with_char_offset + ch_h))
                        pixels_yx = self.get_pixels(cropped, xx + offset_x, yy + offset_y)

                        obj_char = objects.Character(xx + offset_x, yy + offset_y, ch_w + offset_x,
                                                     ch_h + offset_y, char, pixels_yx)
                        obj_word.add_character(obj_char)
                        xx += ch_w + offset_x

                    obj_word.process()
                    obj_box.lines[-1].add_word(obj_word)
                    space_w, space_h = pattern_box.get_text_size(" ")
                    xx += space_w
                obj_box.lines[-1].process()

            if breaked:
                _used_lines = line_idx - 1
            else:
                _used_lines = line_idx + 1

            obj_box.process()
            self.page_objects[-1].add_box(obj_box)
        self.page_objects[-1].process()

    def visualize(self, path_img, path_page_obj, output_destination_path=None, draw_lines=True, draw_words=True, draw_characters=True, visualize=True):
        """
        :param path_img:
        :param path_page_obj:
        :param output_destination_path:
        :param draw_lines:
        :param draw_words:
        :param draw_characters:
        :param visualize:
        :return:
        """
        pg = self.load_page(path_page_obj)

        img = cv2.imread(path_img, -1)
        for box in pg.boxes:
            for line in box.lines:
                if draw_lines:
                    cv2.rectangle(img, (line.x, line.y), (line.x + line.w, line.y + line.h), (0, 0, 255), 2)
                    cv2.circle(img, (line.x, line.y), 5, (0, 0, 255), -1)
                    cv2.circle(img, (line.x + line.w, line.y + line.h), 5, (0, 0, 255), -1)

                for word in line.words:
                    if draw_words:
                        cv2.rectangle(img, (word.x, word.y), (word.x + word.w, word.y + word.h), (255, 0, 0))
                        cv2.circle(img, (word.x, word.y), 4, (255, 0, 0), -1)
                        cv2.circle(img, (word.x + word.w, word.y + word.h), 4, (255, 0, 0), -1)

                    for char in word.characters:
                        if draw_characters:
                            cv2.rectangle(img, (char.x, char.y), (char.x + char.w, char.y + char.h), (0, 255, 0))
                            cv2.circle(img, (char.x, char.y), 3, (0, 255, 0), -1)
                            cv2.circle(img, (char.x + char.w, char.y + char.h), 3, (0, 255, 0), -1)

        if output_destination_path is not None:
            cv2.imwrite(output_destination_path, img)

        if visualize:
            cv2.imshow("Bounding boxes", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
