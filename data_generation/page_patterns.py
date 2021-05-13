#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

from functools import lru_cache

import numpy as np
import random


class PatternBox:
    def __init__(self, x, y, w, h, font, font_size):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = font
        self.font_size = font_size

    def shift_down(self, y_shift):
        self.y += y_shift

    @lru_cache()
    def get_text_size(self, text):
        return self.font.getsize(text)


class Pattern:
    def __init__(self, fonts, pattern_types=["title", "one_column", "two_columns"], font_size=64,
                 resolution_w=None, resolution_h=None, border=60):
        self.allowed_patterns = ["full", "two_columns", "one_column", "two_rows", "zig_zag", "title"]
        self.border = border
        a = set(pattern_types).issubset(self.allowed_patterns )

        if a:
            self.pattern_types = pattern_types
        else:
            print("Unknown pattern type! Pattern type has been set to: full")
            self.pattern_types = ["one_column"]

        # random_norm = np.random.normal(0, 20, 3) + 20
        self.fonts = fonts
        # self.font_size = int((3 + np.random.randint(3, size=1)) * font_size + int(random_norm[0]))
        self.font_size = font_size
        self.resolution_w = resolution_w
        self.resolution_h = resolution_h
        self.pattern_boxes = []

    # def process(self):
    #     for pattern in self.pattern_type:
    #         if pattern == "full":
    #             self.full()
    #         elif pattern == "two_columns":
    #             self.two_columns()
    #         elif pattern == "one_column":
    #             self.one_column()
    #         elif pattern == "two_rows":
    #             self.two_rows()
    #         elif pattern == "zig_zag":
    #             self.zig_zag()
    #         elif pattern == "title_normal":
    #             self.title_normal()
    #         else:
    #             print("Unknown pattern type! Pattern type has been set to: full")
    #             self.full()
    #     return self.pattern_boxes

    def process(self):
        self.add_patterns(self.pattern_types)
        return self.pattern_boxes

    def full(self):
        pattern_box = PatternBox(self.font_size, self.font_size, self.resolution_w - (2 * self.font_size),
                                 self.resolution_h - (2 * self.font_size))
        self.pattern_boxes.append(pattern_box)

    def two_columns(self):
        w = int(self.resolution_w / 2) - (2 * self.font_size)
        h = self.resolution_h - (2 * self.font_size)
        x_right = int(self.resolution_w / 2) + self.font_size

        pattern_box_left = PatternBox(self.font_size, self.font_size, w, h)
        pattern_box_right = PatternBox(x_right, self.font_size, w, h)
        self.pattern_boxes.append(pattern_box_left)
        self.pattern_boxes.append(pattern_box_right)

    def one_column(self):
        w = int(self.resolution_w / 2)
        x = int(self.resolution_w / 4)
        pattern_box = PatternBox(x, self.font_size, w, self.resolution_h - (2 * self.font_size))
        self.pattern_boxes.append(pattern_box)

    def two_rows(self):
        # 1 - full width like "full" and 70 percent height
        # 2 - half width and 28 percent height

        w = self.resolution_w - (2 * self.font_size)
        h = int((self.resolution_h - (2 * self.font_size)) * 0.7)
        h2 = int((self.resolution_h - (2 * self.font_size)) * 0.28)

        pattern_box_upper = PatternBox(self.font_size, self.font_size, w, h)
        pattern_box_bottom = PatternBox(int(w / 2), h + self.font_size, int(w / 2), h2)

        self.pattern_boxes.append(pattern_box_upper)
        self.pattern_boxes.append(pattern_box_bottom)

    def zig_zag(self):
        x1 = self.font_size
        x2 = int(self.resolution_w / 2) + self.font_size
        x3 = x1

        y1 = self.font_size
        y2 = int(self.resolution_h * 0.33)
        y3 = int(self.resolution_h * 0.66)

        w1 = int(self.resolution_w / 2) - 2 * self.font_size
        w2 = w1
        w3 = w1

        h1 = int(self.resolution_h * 0.3)
        h2 = h1
        h3 = h1

        pattern_box_upper = PatternBox(x1, y1, w1, h1)
        pattern_box_midle = PatternBox(x2, y2, w2, h2)
        pattern_box_bottom = PatternBox(x3, y3, w3, h3)

        self.pattern_boxes.append(pattern_box_upper)
        self.pattern_boxes.append(pattern_box_midle)
        self.pattern_boxes.append(pattern_box_bottom)

    def title_normal(self):
        w = int(self.resolution_w / 2)
        h = int(self.font_size / 2)
        y = int(self.resolution_h / 3)
        x = int(self.resolution_w / 4)
        pattern_box = PatternBox(x, y, w, h)
        self.pattern_boxes.append(pattern_box)

    def create_pattern_box(self, pattern):
        pattern_box = []
        if pattern == "title":
            font_size = 4 * self.font_size
            w = int(self.resolution_w) - self.border
            h = int(font_size * 2)
            y = self.border + font_size
            x = self.border + font_size
            font = self.fonts[1]

            pattern_box.append(PatternBox(x, y, w, h, font=font, font_size=font.size))
        elif pattern == "one_column":
            y = self.border + self.font_size
            x = self.border + self.font_size
            w = int(self.resolution_w) - self.border
            h = int(self.resolution_h/4) - (2 * self.font_size)
            pattern_box.append(PatternBox(x, y, w, h,
                                          font=self.fonts[0], font_size=self.font_size))

        elif pattern == "two_columns":
            w = int(self.resolution_w / 2) - (2 * self.font_size)
            h = int(self.resolution_h/4) - (2 * self.font_size)
            x_right = int(self.resolution_w / 2) + self.font_size
            y = self.border + self.font_size
            pattern_box_left = PatternBox(self.border + self.font_size, y, w, h, font=self.fonts[0],
                                          font_size=self.font_size)
            pattern_box_right = PatternBox(self.border + x_right, y, w, h, font=self.fonts[0],
                                           font_size=self.font_size)
            pattern_box.append(pattern_box_left)
            pattern_box.append(pattern_box_right)

        elif pattern == "full":
            pattern_box_full = PatternBox(self.font_size + self.border, self.font_size + self.border, self.resolution_w
                                          - (2 * self.font_size) - 2 * self.border,
                                         self.resolution_h - (2 * self.font_size) -  2 * self.border, font=self.fonts[0],
                                         font_size=self.font_size)
            pattern_box.append(pattern_box_full)


        # elif pattern == "shift_left":
        #
        # elif pattern == "shift_right":

        else:
            # pattern_box = PatternBox(x, y, w, h)
            print('Not supported pattern.')

        return pattern_box

    def add_patterns(self, patterns):
        for pattern in patterns:
            pattern_box = self.create_pattern_box(pattern)

            if not self.pattern_boxes:
                self.pattern_boxes.extend(pattern_box)
            else:
                last_box = self.pattern_boxes[-1]
                y_shift = last_box.y + last_box.h + last_box.font_size
                for item in pattern_box:
                    item.shift_down(y_shift)
                self.pattern_boxes.extend(pattern_box)
