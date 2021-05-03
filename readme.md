Tesseract OCR Training Notes
============================
https://github.com/tesseract-ocr/

No CUDA acceleration, experimental OpenCL acceleration, not worth it.

Getting tesseract and training utilities
----------------------------------------

For training `lstmtrainer` executable is needed:
 - it can be installed using `apt install tesseract-ocr libtesseract-dev`
 - it is NOT included in Linux conda package https://anaconda.org/conda-forge/tesseract
 - it is included in Windows conda package https://anaconda.org/conda-forge/tesseract
 - it can be built from sources in tesseract repository 
    https://tesseract-ocr.github.io/tessdoc/Training-Tesseract.html#building-the-training-tools
 - UB Mannheim provides binaries for Windows https://github.com/UB-Mannheim/tesseract/wiki
 
Training
--------
From https://tesseract-ocr.github.io/tessdoc/TrainingTesseract-4.00.html :
https://tesseract-ocr.github.io/tessdoc/tess4/TrainingTesseract-4.00.html
 
Requirements:

To fine-tune one needs `***.traineddata` as well as ltsm recognition model extracted from it,
suitable pretrained models can be obtained from https://github.com/tesseract-ocr/tessdata_best.
 
To extract all model data from `***.traineddata` use
```
combine_tessdata -u ***.traineddata [output file prefix]
``` 
Only one component can be extracted using option -e which requires name of the existing component e.g.
```
combine_tessdata -e ***.traineddata ltsm
```
The components are:
 - `ltsm`
 - `ltsm-number-dawg`  (patterns of numbers that are allowed)
 - `ltsm-punc-dawg`  (punctuation pattern dawg, patterns of punctuation allowed around words)
 - `ltsm-recorder`  (i.e. Unicharcompress, maps the unicharset further to the codes actually used by the neural network recognizer)
 - `ltsm-unicharset`  
 - `lstm-word-dawg`  (the system word-list language model)
 - `version`
    
The 128 flag turns on Adam optimization, which seems to work a lot better than plain momentum, 
64 allows adaptive learning rate. Default is 192 which allows both.


Training data:
 - images in various formats (.tif and .jpg definetly work)
 - boxfiles in various formats:
   ```
    WordStr <left> <bottom> <right> <top> <page> #<the text of the line>
    \t <left> <bottom> <right> <top> <page>
   ```
      - tab marks end of the line, there must be a space after tab
      - the coordinate system originates in bottom left of the picture
      - in tiff you can have image with multiple pages numbered from zero
 - lstmf files which are generated from images and box files using tesseract itself:
        ```
        tesseract <name>.tiff <name>.box lstm.train
        ```
      - box file and image should have the same name, the file created is name <name>.box.lstmf 
      - box file name actually also acts as base_name
      - lstm.train is config file located in tesseract install folder, it is not present in Windows Conda package
      - setting language model during lstmf generation is not supported
      ? during creation of lstmf files tesseract seemingly tries to segment the image and 
        complains about "No block overlapping textline"
        

Training commands:
```
lstmtraining --model_output <output prefix for checkpoints> \
    --continue_from <path to base checkpoints ***.ltsm or component from ***.traineddata> \
    --traineddata <path to ***.traineddata file> \
    --train_listfile <path list of training lstmf files, actual paths visible from current dir are needed> \
    --eval_listfiles <path list of evaluation lstmf files, actual paths visible from current dir are needed>
    --max_iterations 1200
    
    --debug_interval -1 # prints debug info for every line
```

```
lstmtraining --model_output checkpoints/testtrain3/
    --continue_from tessdata/ces_components/ces.lstm
    --traineddata tessdata/ces.traineddata
    --train_listfile dataset/nesikud_data_tess/files_list.txt
    --max_iterations 100
```

Windows
```
lstmtraining --model_output checkpoints/testtrain2/ --continue_from tessdata/ces_components/ces.lstm --traineddata tessdata/ces.traineddata --train_listfile dataset/nesikud_data_tess_win/files_list.txt --max_iterations 200
```

Combining outputfiles:

```
lstmtraining --stop_training \
  --continue_from ~/tesstutorial/eng_from_chi/base_checkpoint \
  --traineddata <path to ***.traineddata file used in training> \
  --model_output <path for output traineddata file>
```

To test inferece of a finetuned model:

```
tesseract dataset\nesikud_data\UC_cnb000356125-001_0481.jpg \
             <output file base>
             -l <name of the finetuned model> 
             --tessdata-dir <tessdata directory containing finetuned model .traineddata>
```


**TODO? Some transcriptions cant be encoded, why?**

**TODO? CTC loss -- due to bad segmentation**

**TODO? specify tesseract training input and data generation task
        - zachovat ukládání do pickle + tesseract**

Architecture
------------

Architecture in given `***.traineddata` can be obtained by

```
combine_tessdata -d ***.traineddata
```

For ces.traineddata it is:
```
Version string:4.00.00alpha:ces:synth20170629:[1,48,0,1Ct3,3,16Mp3,3Lfys64Lfx96Lrx96Lfx384O1c1]
17:lstm:size=7541987, offset=192
18:lstm-punc-dawg:size=322, offset=7542179
19:lstm-word-dawg:size=3366074, offset=7542501
20:lstm-number-dawg:size=2114, offset=10908575
21:lstm-unicharset:size=7028, offset=10910689
22:lstm-recoder:size=1111, offset=10917717
23:version:size=80, offset=10918828
```

`[1,48,0,1 Ct3,3,16 Mp3,3 Lfys64 Lfx96 Lrx96 Lfx384 O1c1]` describes neural network model in
Variable-size Graph Specification Language (VGSL) (cf. https://tesseract-ocr.github.io/tessdoc/VGSLSpecs):

For `ukr.trainedata` it is:
```
Version string:4.00.00alpha:ukr:synth20170629
17:lstm:size=7446507, offset=192
18:lstm-punc-dawg:size=1986, offset=7446699
19:lstm-word-dawg:size=3403442, offset=7448685
20:lstm-number-dawg:size=530, offset=10852127
21:lstm-unicharset:size=5558, offset=10852657
22:lstm-recoder:size=832, offset=10858215Miscellaneous notes
23:version:size=30, offset=10859047
```

On Ubuntu Tesseract installs into `/usr/share/tesseract-ocr/4.00`, 
one can find data and configs here in subfolders of `tessdata/`.



