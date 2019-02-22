from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request
import time
from detector import Detector
from datautil import DataUtil
from k_mean_clf import KMeanClassifier
import pickle
from camera import *
from threading import Thread
from time import sleep
import operator
from detect_cluster import clusterData
from prepareData import cook
import os

####################
# DEFAULT IMPORTS
####################
du = DataUtil()
det = Detector('cnn')
f = open('../../Data/k_mean_clf.pickle')
clf = pickle.load(f)
session = None  # {id:,list:{id:(id,name,conf)},images:{id:image}}
train = None # {train_session_path:,bins_path,clf_path,[[image_clusters]]}
folderScanOn = False
cameraScanOn = False
tmp_dir = '../../Data/tmp'
#f = open('../../Data/all_Xy_new.pickle')
#X, y = pickle.load(f)
#clf = KMeanClassifier()
#clf.fit(X, y)

####################
#    APP
####################
app = Flask(__name__)
socketio = SocketIO(app) #turn the flask app into a socketio app

@app.route('/')
def index():
    return render_template('index.html')

####################
# Interface
####################

@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

########################
# General Requests
########################
@socketio.on('req',namespace='/test')
def handleReq(data):
    global session,folderScanOn,cameraScanOn
    reqType = data['type']
    print('[req] Got request {}'.format(reqType))

    ####################
    # Take snap from camera feed
    ####################
    if (reqType == 'snapAndRecognize'):
        # if session is None:  take image, classify, call show Image
        # else : take image, classify, update Session, call updateSession, call showImage
        image_dir = (tmp_dir if (session is None) else session['image_dir'])
        image = saveImage(image_dir)
        marked_image = markStudent(image)
        face_lab_image = du.labelFaces2(marked_image)
        enc_image = du.encodeImage(face_lab_image)
        socketio.emit('update', {'image': 'data:image/png;base64,'+enc_image, 'image_id': image.fileName},namespace='/test')

    ####################
    # Session API
    ####################
    elif (reqType == 'startSession'):
        # initiate global session object
        ts = time.time()
        time_string = '%d-%m-%Y_%Hh%Mm'
        st = datetime.datetime.fromtimestamp(ts).strftime(time_string)
        if session is None:
            session = {
                'id' : st,
                'list' : {},
                'images':{},
                'image_dir' : '../../Data/session_images/' + st,
                'out_dir' : './static/' + st
            }
            createDir(session['image_dir'])
            createDir(session['out_dir'])

    elif (reqType == 'endSession'):
        # Call showReport(session)
        session = None

    elif (reqType == 'saveSession'):
        session = None
        # Save csv (LATER)

    ########################
    #   Start/Stop Camera Scan
    ########################
    elif (reqType == 'startCameraScan'):
        cameraScanOn = True
        TourThread().start()

    elif (reqType == 'stopCameraScan'):
        cameraScanOn = False

    ########################
    # Folder Scan On/Off
    ########################
    elif (reqType == 'startFolderScan'):
        folderScanOn = True
        sessions_folder_path = '../../Data/session-eval/'
        FolderScan(sessions_folder_path + data['sessionId']).start()

    elif (reqType == 'stopFolderScan'):
        folderScanOn = False	

########################
# Train requests
########################
@socketio.on('trainReq',namespace='/test')
def handleTrainReq(data):
    global train, clf
    reqType = data['type']
    print('[handleTrainReq] got {} request'.format(reqType))
    if(reqType == 'trainOn'):
        ts = time.time()
        time_string = '%d-%m-%Y_%Hh%Mm'
        st = datetime.datetime.fromtimestamp(ts).strftime(time_string)
        train = {
                'id':st,
                'current_cluster' : [],
                'n_clusters' : 2,
                'image_dir' : '../../Data/train_sessions/' + st,
		'cluster_path': '../../Data/train_sessions/' + st + '/images',  
                'bin_path' : '../../Data/train_sessions/' + st + '/bins'
            }
        createDir(train['image_dir'])
        createDir(train['bin_path'])
        createDir(train['cluster_path'])
    elif(reqType == 'trainOff'):
        train = None

    elif(reqType == 'takeImage'):
        image_dir = (tmp_dir if (train is None) else train['cluster_path'])
        image = saveImage(image_dir)
        enc_image = du.encodeImage(image.getImage())
        socketio.emit('update', {'image': 'data:image/png;base64,'+enc_image, 'image_id':image.fileName},namespace='/test')
        ## take image, add to addPeople variable, update frontend
        if train is not None:
        	train['current_cluster'].append(image)
        print('---')

    elif(reqType == 'cluster'):
        ## run cluster script, send images to frontend
        train["n_clusters"] = data['people']
        # also update num_clusters if needed from frontend
        bins = clusterData(train['current_cluster'], train['bin_path'], train['n_clusters'])
        encs_bins = []
        for i in range(len(bins)):
            encs = []
            for face in bins[i][:4]:
                enc_image = du.encodeImage(face.myFace,1,1)
                encs.append('data:image/png;base64,'+enc_image)
            encs_bins.append(encs)		
        socketio.emit('trainUpdate',{'type':'showClusters','clusters':encs_bins},namespace='/test')
        print('---')
    elif(reqType == 'addPeople'):
        ## get labels, add clusters to train variable
        ls = data['peopleData'] # list of [id, name] pairs in the same order as sent clusters
        base_path = train['bin_path'] + '/bin'
        print(train['n_clusters'])
        for i in range(train['n_clusters']):
        	bin_path = base_path + str(i)
       		print('bin path '+bin_path)
        	if os.path.exists(bin_path):
        		print('renamed {} to {}'.format(bin_path,train['bin_path']+'/'+ls[i][0] + '|' + ls[i][1]))
        		os.rename(bin_path, train['bin_path']+'/'+ls[i][0] + '|' + ls[i][1])
        # update cluster_id and create new directory for current cluster
        train['current_cluster'] = []
    elif(reqType == 'trainClassifier'):
        ## use train variable to get classifier, then send update to frontend
        cook(train['cluster_path'], train['bin_path'])
        clf = KMeanClassifier()
        f = open('../../Data/default_data.pickle')
        X, y = pickle.load(f)
        clf.fit(X, y)
        

# Ally Functions

def createDir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print('[INFO] Directory created.')
        except:
            print('[ERROR] Directory could not be created.')

# session = {id:,list:{id:{id,name,conf},images:{id: [(scores, image)]}}
def updateSession(ls):
	# got [(label, score, face_matrix)]
	for l, sc, face_matrix in ls:
		if l in session['list']:
			session['list'][l]['conf'] += 0.25
			if (len(session['images'][l])<4):
				session['images'][l].append((sc,face_matrix))
				session['images'][l].sort(reverse=True)
			elif (sc > session['images'][l][3][0]):
				session['images'][l][3] = (sc,face_matrix)
				session['images'][l].sort(reverse=True,key=operator.itemgetter(0))
		else:
			if '|' in l:
				name, iden = l.split('|')
				session['list'][l] = {'id': iden, 'name': name, 'conf': 0.25}
			else:
				session['list'][l] = {'id': l, 'name': l, 'conf': 0.25}
			session['images'][l] = [(sc, face_matrix)]

def markStudent(image,update_session=True):
    global session
    faces = det.detect([image])
    labels = ['unknown' for i in range(len(faces))]
    scores  = []
    for i,fac in enumerate(faces):
        ds = clf.candidates(fac.enc,5)
        d1, l1 = ds[0][0], ds[0][1]
        d2, l2 = ds[1][0], ds[1][1]
        if d1 > 0.3:
            sc = d2 - 1.1*d1 -0.01
        else:
            sc = d2-d1-0.04
        scores.append((sc,ds,i))
    scores = sorted(scores)
    scores.reverse()

    for sc,ds,i in scores:
        if sc>0 and ds[0][1] not in labels:
            labels[i] = ds[0][1]

    for i in range(len(labels)):
        faces[i].label = labels[i]

    if (update_session and (session is not None)):
        # [(label, score, face_matrix)]
        ls = [(labels[i], sc, faces[i].myFace) for (sc, ds, i) in scores if labels[i] != 'unknown']
        updateSession(ls)
        print('[markStudent] Sending session update command')
        socketio.emit('update', {'id': session['id'], 'session': {'list':session['list']}},namespace='/test')
    return image

class FolderScan(Thread):
	def __init__(self,folderPath):
		self.folderPath = folderPath
		super(FolderScan,self).__init__()

	def run(self):
		global folderScanOn
		def sort_func(img):
			return int(img.fileName[5:-4])
		images = du.readImages(self.folderPath)		
		#images = sorted(du.readImages(self.folderPath),key=sort_func)
		for i in range(len(images)):
			if folderScanOn==False:
				break
			marked_image = markStudent(images[i])
			face_labelled_image = du.labelFaces2(marked_image)
			enc_image = du.encodeImage(face_labelled_image)
			socketio.emit('update', {'image': 'data:image/png;base64,'+enc_image},namespace='/test')
			sleep(1)

class processImageThread(Thread):
	def __init__(self, image):
		self.image = image
		super(processImageThread,self).__init__()

	def run(self):
		marked_image = markStudent(self.image)
		face_labelled_image = du.labelFaces2(marked_image)
		enc_image = du.encodeImage(face_labelled_image)
		socketio.emit('update', {'image': 'data:image/png;base64,'+enc_image},namespace='/test')


### Tour thread only called once
class TourThread(Thread):
	def __init__(self):
		# Add folderpath for tour
		# out_dir comes from camera.py
		self.imagePath = (tmp_dir if (session==None) else session['image_dir'])
		self.tour = Tour(-1)
		super(TourThread,self).__init__()

	def run(self):
		global cameraScanOn
		tourDone = False
		while (cameraScanOn and (not tourDone)):
			print('[TourThread] Moving on..')
			tourDone = not self.tour.getNext()
			for i in range(2):
				newImage = saveImage(self.imagePath)
				processImageThread(newImage).start()
				time.sleep(1)
			# will get image, process it, save it to static, return filename
			

####################
# Main
####################

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=8081)
    createDir(tmp_dir)
