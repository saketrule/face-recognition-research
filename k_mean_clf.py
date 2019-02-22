# created @akash 22/1/19
# mean classifier

import numpy as np
import pandas as pd
import pickle

class KMeanClassifier:

	def fit(self, X, y):
		y1 = pd.Series(y)
		grps = y1.groupby(y1)

		bins = []; self.bin_map = {}
		for i in y1.unique():
			self.bin_map[len(bins)] = i
			bins.append(list(grps.groups[i]))

		train_bins = []


		for i in range(len(bins)):
			train_bins.append(np.array([X[j] for j in bins[i]]))

		self.train_bins = train_bins	

	def get_dist(self, e1, e2):
		return np.linalg.norm(e1 - e2)

	def get_score(self,e1,bin, k = 10):
		dist = np.linalg.norm(bin - e1,axis=1)
		return np.mean(sorted(dist)[:k])

	def predict(self, enc, k):
		dists = [self.get_score(enc,bin, k) for bin in self.train_bins]
		lab = np.argmin(dists)
		# check with threshold
		# if(dists[lab] > thresh[lab]):
		# 	lab = -1
		return self.bin_map[lab], dists[lab], dists

	def candidates(self, enc, k):
		dists = [self.get_score(enc,bin, k) for bin in self.train_bins]
		lab_dist = [(dists[i], self.bin_map[i]) for i in range(len(dists))]
		return sorted(lab_dist)

# f = open('../../../Data/all_Xy.pickle','r+')
# X, y = pickle.load(f)
# mc = KMeanClassifier()
# mc.fit(X, y)
# with open('../../../Data/mean_k_clf.pickle','w+') as f:
# 	pickle.dump(mc, f)

# train()


