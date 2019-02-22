# created @akash 22/1/19
# code contains
# detect - cluster - write bins
# to set
# n_clusters, BIN_PATH, in_dir 

from detector import Detector
from datautil import DataUtil
from sklearn.cluster import KMeans
import numpy as np
import sys

du = DataUtil()
# n_clusters = 1
# in_dir = '../../Data/33'
# BIN_PATH = '../../Data/FINAL_DATASET/'	

# n_clusters = int(sys.argv[1])
# in_dir = sys.argv[2]
# BIN_PATH = sys.argv[3]

def clusterData(images, BIN_PATH, n_clusters):
	print '[Detecting faces]'	
	# detect faces
	det = Detector('cnn')
	# images = du.readImages(in_dir)
	faces = det.detect(images)

	print '[Generating clusters]'
	# cluster
	X = [face.enc for face in faces]
	kmeans = KMeans(n_clusters, random_state = 2).fit(X)
	face_labels = kmeans.labels_

	print '[Saving bins]'
	# script to save images from bins
	for i in range(len(images)):
		for j in range(len(images[i].faces)):
			images[i].faces[j].indexInImage = j
	bins = [[] for i in range(n_clusters)]
	for i in range(len(face_labels)):
		bins[face_labels[i]].append(faces[i])
	du.writeBins(bins, BIN_PATH)
	print '[Done]'
	return bins