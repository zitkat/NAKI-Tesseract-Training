#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

import numpy as np
import cv2
import _pickle as pickle
import _functools as functools


#def noisy(noise_typ, image):
#    if noise_typ == "gauss":
#        row, col = image.shape
#        mean = 0
#        var = 0.1
#        sigma = var ** 0.5
#        n = 8
#        rrow = np.uint(np.floor(row/n))
#        ccol = np.uint(np.floor(col/n))
#        gauss = 255.0 * np.random.normal(mean, sigma, (rrow, ccol))
#        gauss = cv2.resize(gauss, (col, row), interpolation=cv2.INTER_LINEAR)
#        # gauss = np.resize(gauss, (row, col))
#        noi = image.astype(np.float32) + gauss
#        noi[noi > 255] = 180
#        noi[noi < 0] = 15 + np.random.random_integers(0, 10, 1)
#        return noi.astype(np.uint8)

#    elif noise_typ == "s&p":
#        row, col = image.shape
#        s_vs_p = 0.5
#        amount = 0.004
#        out = np.copy(image)
#        # Salt mode
#        num_salt = np.ceil(amount * image.size * s_vs_p)
#        coords = [np.random.randint(0, i - 1, int(num_salt))
#                  for i in image.shape]
#        out[coords] = 1

#        # Pepper mode
#        num_pepper = np.ceil(amount * image.size * (1. - s_vs_p))
#        coords = [np.random.randint(0, i - 1, int(num_pepper))
#                  for i in image.shape]
#        out[coords] = 0
#        return out

#    elif noise_typ == "poisson":
#        vals = len(np.unique(image))
#        vals = 2 ** np.ceil(np.log2(vals))
#        noisy = np.random.poisson(image * vals) / float(vals)
#        return noisy
#    elif noise_typ == "speckle":
#        row, col = image.shape
#        gauss = np.random.randn(row, col)
#        gauss = gauss.reshape(row, col)
#        noisy = image + image * gauss
#        return noisy
#    else:
#        print ("unknown noise mode")


#def combine_images(img_text, img_background):
#    ret, mask_inv = cv2.threshold(img_text, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#    mask = cv2.bitwise_not(mask_inv)

#    img_noise = noisy("gauss", img_text)
#    img_noise8 = np.uint8(img_noise)
#    img_noise3ch = cv2.cvtColor(img_noise8, cv2.COLOR_GRAY2BGR)
#    img_noise3ch = cv2.blur(img_noise3ch, (3, 3))

#    img1_bg = cv2.bitwise_and(img_background, img_background, mask=mask_inv)
#    img2_fg = cv2.bitwise_and(img_noise3ch, img_noise3ch, mask=mask)

#    dst = cv2.add(img1_bg, img2_fg)
#    dst2 = cv2.blur(dst, (3, 3))

#    return dst2

def noisy(noise_typ, image, var=0.3):
    if noise_typ == "gauss":
        row, col = image.shape
        mean = 0
        sigma = var ** 0.5
        n = 8  # MAGIC?
        rrow = np.uint(np.floor(row/n))
        ccol = np.uint(np.floor(col/n))
        gauss = 255.0 * np.random.normal(mean, sigma, (rrow, ccol))
        gauss = cv2.resize(gauss, (col, row), interpolation=cv2.INTER_LINEAR)
        # gauss = np.resize(gauss, (row, col))
        noi = image.astype(np.float32) + gauss
        noi[noi > 255] = 255
        noi[noi < 0] = 0
        # noi[noi > 255] = 180
        # noi[noi < 0] = 15 + np.random.random_integers(0, 10, 1)
        return noi.astype(np.uint8)

    else:
        print("unknown noise mode")


def combine_images(img_foreground, img_background, var=0.3, blur_kernel=(7, 7)):
    # img_foreground = noisy("gauss_add_black", img_foreground)
    ret, mask = cv2.threshold(img_foreground, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    img_noise = noisy("gauss", img_foreground, var)
    img_noise8 = np.uint8(img_noise)
    img_noise3ch = cv2.cvtColor(img_noise8, cv2.COLOR_GRAY2BGR)
    img_noise3ch = cv2.blur(img_noise3ch, blur_kernel)
    alpha = cv2.cvtColor(img_noise3ch, cv2.COLOR_BGR2GRAY)
    alpha = cv2.bitwise_and(alpha, alpha, mask=mask)

    h, w = img_foreground.shape
    out = np.zeros(img_background.shape, dtype=img_background.dtype)
    #for i in range(h):
    #    for j in range(w):
    #        a = float(alpha[i][j] / 255.0)
            #out[i][j] = a * img_background[i][j]
            #if a == 0:
            #    out[i][j] += img_background[i][j]

    alpha = cv2.merge((alpha, alpha, alpha)) / 255.0
    out[alpha > 0] = alpha[alpha > 0] * img_background[alpha > 0]
    out[alpha == 0] += img_background[alpha == 0]

    return cv2.blur(out, (5, 5))

def load_page(page_path):
    with open(page_path, 'rb') as pickle_file:
        pg = pickle.load(pickle_file)
    return pg


def save_page(page_path, page):
    with open(page_path, 'wb') as pickle_file:
        pickle.dump(page, pickle_file)


def save_page_teseract(page_path, page):
    with open(page_path, 'w', encoding='utf_8') as txt_file:
        for box in page.boxes:
            for line in box.lines:
                for words in line.words:
                    for character in words.characters:
                        txt_file.write(character.character + " " + str(line.x) + " " + str(page.resolution_h - (line.y + line.h))
                                       + " " + str(line.x + line.w) + " " + str(page.resolution_h - line.y)
                                       + " 0" + "\n")
                    txt_file.write(" " + " " + str(line.x) + " " + str(page.resolution_h - (line.y + line.h))
                                   + " " + str(line.x + line.w) + " " + str(page.resolution_h - line.y)
                                   + " 0" + "\n")
                txt_file.write("\t" + " " + str(line.x) + " " + str(page.resolution_h - (line.y + line.h))
                               + " " + str(line.x + line.w) + " " + str(page.resolution_h - line.y)
                               + " 0" + "\n")



def tune_size(roi, original_x, original_y, min_contour_size):
    # ret, thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    thresh = ((roi < 255)*255).astype(np.uint8)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cont = []
    for c in contours:
        if len(c) > min_contour_size:
            cont.append(c)

    if len(cont) > 0:
        new_cnt = functools.reduce(lambda x, y: np.concatenate((x, y)), cont)
        x, y, w, h = cv2.boundingRect(np.array(new_cnt))
        return original_x + x, original_y + y, w, h
    else:
        return original_x, original_y, roi.shape[1], roi.shape[0]


def fine_tuning(page_path, page_name, img_text_path, min_contour_size):
    pg = load_page(page_path + page_name)
    img = cv2.imread(img_text_path, 0)

    for box in pg.boxes:
        for line in box.lines:
            roi = img[line.y:(line.y + line.h), line.x:(line.x + line.w)]
            line.x, line.y, line.w, line.h = tune_size(roi, line.x, line.y, min_contour_size)

            for word in line.words:
                roi = img[word.y:(word.y + word.h), word.x:(word.x + word.w)]
                word.x, word.y, word.w, word.h = tune_size(roi, word.x, word.y, min_contour_size)

                for char in word.characters:
                    roi = img[char.y:(char.y + char.h), char.x:(char.x + char.w)]
                    char.x, char.y, char.w, char.h = tune_size(roi, char.x, char.y, min_contour_size)

    save_page(page_path + "page_obj_tuned.pickle", pg)


def fine_tuning_onfly(pg, img, min_contour_size):
    for box in pg.boxes:
        for line in box.lines:
            roi = img[line.y:(line.y + line.h), line.x:(line.x + line.w)]
            line.x, line.y, line.w, line.h = tune_size(roi, line.x, line.y, min_contour_size)

            for word in line.words:
                roi = img[word.y:(word.y + word.h), word.x:(word.x + word.w)]
                word.x, word.y, word.w, word.h = tune_size(roi, word.x, word.y, min_contour_size)

                for char in word.characters:
                    roi = img[char.y:(char.y + char.h), char.x:(char.x + char.w)]
                    char.x, char.y, char.w, char.h = tune_size(roi, char.x, char.y, min_contour_size)

    return pg
