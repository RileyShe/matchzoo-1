data_path="/Data/work/xliu93/stackoverflow/MatchZoo_data/stackOF/"$1_$2"/"
code_path="/Data/work/xliu93/stackoverflow/MatchZoo/data/stackOF/"
glove_dir="/Data/work/xliu93/stackoverflow/MatchZoo_data/glove_backup/"

# download the wiki-qa dataset

#cd $data_path
#wget https://download.microsoft.com/download/E/5/F/E5FCFCEE-7005-4814-853D-DAA7C66507E0/WikiQACorpus.zip
#unzip WikiQACorpus.zip
#
## download the glove vectors
#
#wget http://nlp.stanford.edu/data/glove.840B.300d.zip
#unzip glove.840B.300d.zip
#wget http://nlp.stanford.edu/data/glove.6B.zip
#unzip glove.6B.zip

# filter queries which have no right or wrong answers
#python filter_query.py

# transfer the dataset into matchzoo dataset format
#python transfer_to_mz_format.py
# generate the mz-datasets

cd $code_path
python prepare_mz_data.py $1 $2

# generate word embedding

array=( 50 100 200 300 )
for i in "${array[@]}"
do
	if [[ $3 -eq wikiqa ]]; then
		fold_name="glove_general"
		filename="glove.6B."${i}"d.txt"
	else:
		fold_name="glove_stackOF"
		filename="gensim_glove_"${i}"d.txt"
	fi
        python gen_w2v.py ${glove_dir}/${fold_name}/${filename} ${data_path}/word_dict.txt ${data_path}/embed_glove_d${i}
        python norm_embed.py ${data_path}/embed_glove_d${i} ${data_path}/embed_glove_d${i}_norm
done

# generate data histograms for drmm model
# generate data bin sums for anmm model
# generate idf file
cat ${data_path}word_stats.txt | cut -d ' ' -f 1,4 > ${data_path}embed.idf
python gen_hist4drmm.py 60 $data_path
python gen_binsum4anmm.py 20 $data_path # the default number of bin is 20

echo "Done ..."