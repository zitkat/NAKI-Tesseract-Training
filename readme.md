# Tesseract OCR Training for NAKI-NKVD

This repostiroy contains tooling and neccesary information for finetuning 
Tesseract v4 on cutom data.


## Contents
* [Structure](#structure)
* [Installation](#installation)
* [Tesseract Training](#tesseract-training)

## Structure
```
.
├── checkpoints                        - output dir for tesseract cechkpoints and training and eval outputs
├── data_annot                         - tools for processing annotated data from CVAT
├── data_generation                    - synthetic data generation code and its outputs
├── data_nesikud                       - tools for processing example data from NESIKUD
├── examples_boxfiles                  - examples of data files needed for training
├── tessdata                           - tessdata dir with config files copied from linux installation, 
|                                      - put ***.trained data models here
├── training_command.ps1               - script with all stages of training: train, export, eval
├── convert_nesikud.py                 - use tool in data_nesikud to create tesseract training data
├── cutout_annotations.py              - use tools from data_annot to to create evaluation cutouts
├── prepare_tesseract_training.py      - create lstmf training files from images and box files
├── tesseval.py                        - evaluate exoprted tesseract model on cutout data
├── testinfer.py                       - single image inference
├── util.py                            - util
├── env_setup.cmd                      - commands to set up conda enviroment on Windows
└── readme.md                          :-)
```

## Installation

Use commands in `env_setup.cmd` to install neccesary packages for tesseract training 
and evaluation into your conda environment. Note however that this is tested only on
Windows and is not complete, see [Tesseract Training](#tesseract-training) bellow
for details on how to get  everything tesseract needs for training.

### Data generation
**TBA:** Data generation has separate set of requirements, namely TensorFlow 1.x.


## Tesseract training

https://github.com/tesseract-ocr/

No CUDA acceleration, experimental OpenCL acceleration, not worth it.

### Getting tesseract and training utilities

For training `lstmtrainer` executable is needed:
 - it can be installed using `apt install tesseract-ocr libtesseract-dev`
 - it **is NOT** included in Linux conda package https://anaconda.org/conda-forge/tesseract
 - it **is** included in Windows conda package https://anaconda.org/conda-forge/tesseract
 - it can be built from sources in tesseract repository 
    https://tesseract-ocr.github.io/tessdoc/Training-Tesseract.html#building-the-training-tools
 - UB Mannheim provides binaries for Windows https://github.com/UB-Mannheim/tesseract/wiki
 

From https://tesseract-ocr.github.io/tessdoc/tess4/TrainingTesseract-4.00.html
(Note that during creation of this repository Tesseract 5.0 has been officially released
and a lot of documentation have been moved)
 
### Pretrained model:

To fine-tune one needs `***.traineddata` as well as `ltsm` recognition model extracted from it,
suitable pretrained models can be obtained from https://github.com/tesseract-ocr/tessdata_best.
 
To extract all model data from `***.traineddata` use
```
combine_tessdata -u ***.traineddata [output file prefix, including folder name]
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
 - `ltsm-unicharset` (set of characters actually recognized)
 - `lstm-word-dawg`  (the system word-list language model)
 - `version`

Example:
````
combine_tessdata -u rus.traineddata rus_components/rus
````
    

### Training data:
 - **images** in various formats (.tif and .jpg definetly work)
 - **boxfiles** in various formats:
   
   WordString box:
   ```
    WordStr <left> <bottom> <right> <top> <page> #<the text of the line>
    \t <left> <bottom> <right> <top> <page>
   ```
   and test2image box, each char in text line on separate line but coordinets of the 
   text line the same for each:
   ```
   <char> <left> <bottom> <right> <top> <page>
   ...
   \t <left> <bottom> <right> <top> <page>
   ```
   were tested, note that:
      - tab marks end of the line, there must be a space after tab
      - the coordinate system originates in bottom left of the picture
      - in tiff you can have image with multiple pages numbered from zero 

   See `example_boxfiles` for, well, examples.
 - **lstmf** files which are generated from images and box files using tesseract itself:
        ```
        tesseract <name>.tiff <name>.box lstm.train
        ```
      - box file and image should have the same name, the file created is named <name>.box.lstmf 
      - box file name actually also acts as base_name
      - lstm.train is config file located in `tessdata/configs` , it is not present in Windows Conda package, you can find in `tessdata/configs` folder in this repository
      - setting language model during lstmf generation is not supported
      - during creation of lstmf files tesseract seemingly tries to segment the image and 
        complains about "No block overlapping textline"
        


### Training commands:

See `training_command.ps1` for example training in PowerShell with duplexed output, 
it should be easily transferable to Linux too.

`net_mode` flag:
>The 128 flag turns on Adam optimization, which seems to work a lot better than plain momentum, 
>64 allows adaptive learning rate. Default is 192 which allows both.

i.e. training uses adam with adaptive training rate by default.
```
lstmtraining --model_output <output prefix for checkpoints> \
    --continue_from <path to base checkpoints ***.ltsm i.e. the component from ***.traineddata> \
    --traineddata <path to ***.traineddata file> \
    --train_listfile <path to list of training lstmf files, actual paths visible from current dir are needed> \
    --eval_listfiles <path to list of evaluation lstmf files, actual paths visible from current dir are needed>
    --max_iterations 1200
    
    --debug_interval -1 # prints debug info for every line
```


Evaulate on data in the same format as training data:
```
lstmeval --model <path chckpoint file from training> `
         --traineddata  <path to ***.traineddata file used in training> `
         --eval_listfile <path to list of evaluation lstmf files, actual paths visible from current dir are needed> `
```

Export checkpoint from training
```
lstmtraining --stop_training \
  --continue_from <path chickpoint file from training> \
  --traineddata <path to ***.traineddata file used in training> \
  --model_output <path for output traineddata file>
```

Evaulate on cutout data:
```
python tesseval.py --dataset-path <path to dataset directory> `
                   --tessdata-path <path to tessdata folder with exported finetuned model> `
                   --model-name <name of the model in <name>.traineddata>`
                   --output-path <where to put output csv with stats>
```

## LSTM Architecture

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
Variable-size Graph Specification Language (VGSL) (cf. https://tesseract-ocr.github.io/tessdoc/tess4/VGSLSpecs.html):

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



