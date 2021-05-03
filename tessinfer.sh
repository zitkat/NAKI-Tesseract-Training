#!/usr/bin/env bash
filename=$1

tesseract "dataset/nesikud_data/$filename" \
          "output/$filename" \
           
