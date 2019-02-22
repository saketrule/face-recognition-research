# created @akash 22/1/19
# generate X, y from bins
# to set 
# in_dir: directory where all root images are present
# folder_path: directory of bins

import numpy as np
import pickle
from datautil import DataUtil
import os
from detector import Detector
import sys

# in_dir = sys.argv[1]
# folderPath = sys.argv[2]

du = DataUtil()
# in_dir = '../../Data/test'
# folderPath = '../../Data/test_bins'
# X = [];	y = []

def cook(in_dir, folderPath):
	print '[Getting bins]'
	# Get image objects from raw images
	det = Detector('cnn')
	images = du.readImages(in_dir)
	faces = det.detect(images)

	# Get X, y
	bins, faces, X, y = du.getTruthFromFolder2(folderPath, images)
	print '[Almost done :) ]'
	with open('../../Data/default_data.pickle','w+') as f:
		pickle.dump((X,y), f)
	print '[Done. Saved as \'default_data.pickle\'.]'