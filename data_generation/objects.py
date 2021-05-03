#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

from operator import attrgetter


class Character:
    def __init__(self, x=0, y=0, w=0, h=0, character=None, pixels_yx=None):
        """
        :type character: char
        """
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.character = character
        self.pixels_yx = pixels_yx

    def print_character(self):
        print (self.character)

    def get_character(self):
        return self.character


class Word:
    def __init__(self, x=0, y=0, w=0, h=0, characters=None, belong_to_sentence=None):
        """
        :type characters: Character
        """
        if characters is None:
            characters = []
        if belong_to_sentence is None:
            belong_to_sentence = -1
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.characters = characters
        self.belong_to_sentence = belong_to_sentence

    def add_character(self, character):
        self.characters.append(character)

    def process(self):
        self.x = self.characters[0].x
        self.w = (self.characters[-1].x + self.characters[-1].w) - self.characters[0].x

        char = min(self.characters, key=attrgetter("y"))
        self.y = int(char.y)

        h_max = 0
        for char in self.characters:
            if (char.y + char.h) > h_max:
                h_max = char.y + char.h
        self.h = int(h_max - self.y)

    def print_word(self):
        text = ""
        for ch in self.characters:
            text += ch.character
        print (text)

    def get_word(self):
        text = ""
        for ch in self.characters:
            text += ch.character
        return text


class Line:
    def __init__(self, x=0, y=0, w=0, h=0, words=None):
        """
        :type words: Word
        """
        if words is None:
            words = []
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.words = words

    def add_word(self, word):
        self.words.append(word)

    def process(self):
        self.x = self.words[0].x
        self.w = (self.words[-1].x + self.words[-1].w) - self.words[0].x

        word = min(self.words, key=attrgetter("y"))
        self.y = int(word.y)

        h_max = 0
        for word in self.words:
            if (word.y + word.h) > h_max:
                h_max = word.y + word.h
        self.h = int(h_max - self.y)

    def get_line(self):
        text = ""
        for word in self.words:
            for char in word.characters:
                text += char.character
            text += " "
        text = text[:-1]
        return text

    def print_line(self):
        print (self.get_line())


class Box:
    def __init__(self, x=0, y=0, w=0, h=0, lines=None):
        """
        :type lines: Lines
        """
        if lines is None:
            lines = []
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.lines = lines

    def add_line(self, line):
        self.lines.append(line)

    def process(self):
        if len(self.lines) != 0:
            self.x = self.lines[0].x
            self.y = self.lines[0].y

            w_max = 0
            for line in self.lines:
                if line.w > w_max:
                    w_max = line.w
            self.w = w_max

            self.h = (self.lines[-1].y + self.lines[-1].h) - self.lines[0].y
        else:
            print("    - Warning: empty box!")
            self.x = 0
            self.y = 0
            self.w = 0
            self.h = 0

    def print_all_sentences(self):
        sentences = []
        sentence = ""
        n = 0
        for line in self.lines:
            for word in line.words:

                if word.belong_to_sentence == n:
                    sentence += word.get_word()
                    sentence += " "

                else:

                    sentences.append(sentence)
                    sentence = ""
                    n += 1

                    sentence += word.get_word()
                    sentence += " "

        sentences.append(sentence)

        for i, sntc in enumerate(sentences):
            print (i, sntc)

    def get_text(self):
        text = ""
        for line in self.lines:
            text += line.get_line()
            text += " "
        return text[:-1]


class Page:
    def __init__(self, x=0, y=0, w=0, h=0, pattern_type="full", boxes=None, res_w=0, res_h=0):
        """
        :type boxes: Boxes
        """
        if boxes is None:
            boxes = []
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.pattern_type = pattern_type
        self.boxes = boxes
        self.page_resolution_w = res_w
        self.page_resolution_h = res_h

    def add_box(self, box):
        self.boxes.append(box)

    def process(self):
        if len(self.boxes) != 0:
            min_x = 9999999
            min_y = 9999999
            max_w = -1
            max_h = -1


            # word = min(self.words, key=attrgetter("y"))
            # self.y = word.y

            for b in self.boxes:
                if b.x < min_x:
                    min_x = b.x
                if b.y < min_y:
                    min_y = b.y
                if (b.x + b.w) > max_w:
                    max_w = (b.x + b.w)
                if (b.y + b.h) > max_h:
                    max_h = (b.y + b.h)

            self.x = min_x
            self.y = min_y
            self.w = max_w - self.x
            self.h = max_h - self.y
        else:
            print("     Warning: empty box!")
            self.x = -1
            self.y = -1
            self.w = -1
            self.h = -1

