#python matchzoo/main.py --phase train --model_file configs/$1/$2.tit.config
python matchzoo/main.py --phase train --model_file configs/$1/$2.ques.config
python matchzoo/main.py --phase train --model_file configs/$1/$2.ans.config

