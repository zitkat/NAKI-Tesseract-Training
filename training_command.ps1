
$RUN_NAME="synth_rus3"
$DATA_NAME="rus1"
$LANG="rus"
$MAX_ITERATION=3000

mkdir -F checkpoints/$RUN_NAME/
cp training_command.ps1 checkpoints/$RUN_NAME

lstmtraining --model_output checkpoints/$RUN_NAME/ `
             --continue_from tessdata/"$LANG"_components/$LANG.lstm `
             --traineddata tessdata/$LANG.traineddata `
             --train_listfile .\data_generation\outputs\"$DATA_NAME"_train\lstmf\files_list.txt `
             --eval_listfile .\data_generation\outputs\"$DATA_NAME"_val\lstmf\files_list_full.txt `
             --max_iterations $MAX_ITERATION `
             2>&1 | tee checkpoints/$RUN_NAME/train_log.txt

lstmtraining --stop_training `
             --continue_from  checkpoints/$RUN_NAME/_checkpoint `
             --traineddata  tessdata/$LANG.traineddata `
             --model_output tessdata/$RUN_NAME.traineddata


lstmeval --model checkpoints/$RUN_NAME/_checkpoint `
         --traineddata  tessdata/$LANG.traineddata `
         --eval_listfile .\data_generation\outputs\"$DATA_NAME"_val\lstmf\files_list_10.txt `
         2>&1 | tee checkpoints/$RUN_NAME/eval_log10.txt

python tesseval.py --dataset-path data_annot/task_typewritten_2_cut `
                   --tessdata-path tessdata `
                   --model-name $RUN_NAME `
                   --output-path checkpoints/$RUN_NAME
