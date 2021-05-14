
$RUN_NAME="annot_tt2_synth_rus1_v1_1_v0_0"
$DATA_NAME="task_typewritten_2_cut_filtered/1"
$DATASETROOT="D:/Datasets/NAKI/annotated"
$LANG="rus"
$MAX_ITERATION=3000

mkdir -F checkpoints/$RUN_NAME/
cp training_annot_command.ps1 checkpoints/$RUN_NAME

lstmtraining --model_output checkpoints/$RUN_NAME/ `
             --continue_from checkpoints/synth_rus1_v1_1/_checkpoint `
             --traineddata tessdata/$LANG.traineddata `
             --train_listfile "${DATASETROOT}/${DATA_NAME}/lstmf/files_list.txt" `
             --max_iterations $MAX_ITERATION `
             2>&1 | tee checkpoints/$RUN_NAME/train_log.txt

lstmtraining --stop_training `
             --continue_from  checkpoints/$RUN_NAME/_checkpoint `
             --traineddata  tessdata/$LANG.traineddata `
             --model_output tessdata/$RUN_NAME.traineddata

python tesseval.py --dataset-path D:\Datasets\NAKI\annotated\task_typewritten_2_cut_filtered/more/ `
                   --tessdata-path tessdata `
                   --model-name $RUN_NAME `
                   --output-path checkpoints/$RUN_NAME
