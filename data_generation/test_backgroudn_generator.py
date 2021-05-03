#!/usr/bin/env python

__author__ = "Lukas Bures"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

from background_generator import *
import cv2


bg_gen_model = load_model("./data/models/vae_naki_wo_060218.h5")
scale = 0.15

img = get_background(bg_gen_model, scale)

cv2.imwrite("./data/test_outputs/bg_gen.png", img)

print ("DONE")
