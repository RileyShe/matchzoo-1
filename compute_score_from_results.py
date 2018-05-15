import sys, math

def score2labellist(y_true, y_pred):
	idx2pred = dict([(x, y_pred[x]) for x in range(0, len(y_pred))])
	idx2true = dict([(x, y_true[x]) for x in range(0, len(y_true))])
	sortedidx2pred = sorted(idx2pred.items(), key = lambda x:x[1], reverse=True)
	labellist = []
	for i in range(0, len(sortedidx2pred)):
		idx = sortedidx2pred[i][0]
		thislabel = idx2true[idx]	
		labellist.append(str(thislabel))
	return labellist

def eval_score(y_true, y_pred, eval_name):
	labellist = score2labellist(y_true, y_pred)
	if eval_name == "mrr":
		return mrr(labellist)
	elif eval_name == "ndcg@10":
		return ndcg(labellist, 10)
	elif eval_name == "ndcg@100":
		return ndcg(labellist, 100)

def mrr(labellist):
        score =0
        scorecount = 0
        for i in range(0, len(labellist)):
                if labellist[i] == "1":
                        score += 1.0 / (i + 1.0)
                        scorecount += 1
        if scorecount == 0:
                return 0
        else:
                return score / scorecount

def ndcg(labellist, topK):
        dcg = idcg = 0.0
        for i in range(0, min(topK, len(labellist))):
                if labellist[i] == "1":
                        dcg += 1.0 / math.log(float(i + 2), 2.0)
        relcount = 0
        for i in range(0, len(labellist)):
                if labellist[i] == "1":
                        relcount += 1
        for i in range(0, min(topK, relcount)):
                idcg += 1.0 / math.log(float(i + 2), 2.0)
	return dcg / idcg

def load_qid2result(lang, component):
	fin = open("../MatchZoo_data/result/" + lang + "/dssm." + component + ".txt", "r")
	conc2score = {}
	conc2gt = {}
	for line in fin:
		tokens = line.strip("\n").split("\t")
		id1 = tokens[0]
		id2 = tokens[2]
		score = float(tokens[4])
		gt = tokens[6]
		conc_id = id1 + "_" + id2
		conc2score[conc_id] = score
		conc2gt[conc_id] = gt
	return conc2score, conc2gt

def load_qid_cosidf(lang):
	testset = set()
	fin = open("../MatchZoo_data/stackOF/data_" + lang + "/" + lang + "_test_qid.txt", "r")

	for line in fin:
		testset.add(line.strip("\n"))
	fin = open("../MatchZoo_data/stackOF/data_" + lang + "/" + lang + "_cosidf.txt", "r")
	qid2qid2list = {}
	qid2gtlist = {}
	fin.readline()
	for line in fin:
		tokens = line.strip("\n").split("\t")
		qid1 = tokens[0]		
		if qid1 not in testset:
			continue
		qid2 = tokens[1]
		gt = tokens[3]
		qid2qid2list.setdefault(qid1, [])
		qid2qid2list[qid1].append(qid2)
		qid2gtlist.setdefault(qid1, [])
		qid2gtlist[qid1].append(gt)
	return qid2qid2list, qid2gtlist

def load_idmap(lang, component):
	fin = open("../MatchZoo_data/stackOF/" + lang + "_" + component + "/idmap1.txt", "r")
	qid2idval1 = {}
	for line in fin:
		tokens = line.strip("\n").split("\t")
		qid = tokens[0]
		idval = tokens[1]
		qid2idval1[qid] = idval
	fin = open("../MatchZoo_data/stackOF/" + lang + "_" + component + "/idmap2.txt", "r")
	qid2idval2 = {}
	for line in fin:
		tokens = line.strip("\n").split("\t")
		qid = tokens[0]
		idval = tokens[1]
		qid2idval2[qid] = idval
	return qid2idval1, qid2idval2

def get_component_score(idmap1, idmap2, qid2qidlist, conc2score, conc2gts):
	qid2scorelist = {}
	qid2gtlist = {}
	for qid1 in qid2qidlist.keys():
		id1 = idmap1[qid1]
		qidlist = qid2qidlist[qid1]
		scorelist = []
		gtlist = []
		for qid2 in qidlist:
			id2 = idmap2[qid2]
			conc_id = id1 + "_" + id2
			score = conc2score[conc_id]
			gt = conc2gts[conc_id]
			scorelist.append(score)
			gtlist.append(gt)
		qid2scorelist[qid1] = scorelist
		qid2gtlist[qid1] = gtlist
	return qid2scorelist, qid2gtlist	

def compare_score_gt(qid2gtlist, qid2gtlist_2, qid2scorelist, metric):
	totalscore = 0
	scorecount = 0
	for qid in qid2gtlist.keys():
		gtlist = qid2gtlist[qid]
		scorelist = qid2scorelist[qid]
		thisscore = eval_score(gtlist, scorelist, metric)
		totalscore += thisscore
		scorecount += 1
	return totalscore / scorecount

def main(argv):
	qid2y_true = {}
	qid2y_pred = {}
	lang = sys.argv[1]
	metric = sys.argv[2]
	components = ["title"]
	coeffs = [1.0]
	qid2qid2list, qid2gtlist = load_qid_cosidf(lang)
	avgscore = 0
	for component in components:
		idmap1, idmap2 = load_idmap(lang, component)
		conc2score, conc2gts = load_qid2result(lang, component)
		qid2scorelist, qid2gtlist_2 = get_component_score(idmap1, idmap2, qid2qid2list, conc2score, conc2gts)	
		avgscore = compare_score_gt(qid2gtlist, qid2gtlist_2, qid2scorelist, metric)
	print(avgscore)
	
if __name__=='__main__':
	main(sys.argv)	
