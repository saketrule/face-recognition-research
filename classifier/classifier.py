from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc
import sys
import os
import argparse
import tensorflow as tf
import numpy as np
import facenet
import align.detect_face
import random
from time import sleep
import math
import pickle

pnet,rnet,onet = None,None,None

def get_faces(img,model_path='./models/20180402-114759/20180402-114759.pb'):
    args = {
        'gpu_memory_fraction':0.25,
        'margin':44,
        'image_size':160
    }
    minsize = 20 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor
    det_threshold = 0.95
    global pnet,rnet,onet
    if pnet is None:
        print('Creating networks and loading parameters for mtnn')
        with tf.Graph().as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=args['gpu_memory_fraction'])
            sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            with sess.as_default():
                pnet, rnet, onet = align.detect_face.create_mtcnn(sess, None)

    img_size = np.asarray(img.shape)[0:2]
    bounding_boxes,_ = align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
    
    # here thresholding only images with high confidence values
    det = [bb[0:4] for bb in bounding_boxes if bb[4]>det_threshold]
    det_arr = [np.squeeze(det[i]) for i in range(len(det))]
    faces = []
    for i, det in enumerate(det_arr):
        det = np.squeeze(det)
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0]-args['margin']/2, 0)
        bb[1] = np.maximum(det[1]-args['margin']/2, 0)
        bb[2] = np.minimum(det[2]+args['margin']/2, img_size[1])
        bb[3] = np.minimum(det[3]+args['margin']/2, img_size[0])
        cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
        scaled = misc.imresize(cropped, (args['image_size'], args['image_size']), interp='bilinear')
        faces.append(scaled)
    # If you want to see a face: misc.imshow(faces[-4])

    with tf.Graph().as_default():
    
        with tf.Session() as sess:
            
            #np.random.seed(seed=666)  ## Saket - add a randm seed here; not using random
            
            # Load the model
            print('Loading feature extraction model')
            facenet.load_model(model_path)
            
            
            # Get input and output tensors
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
            embedding_size = embeddings.get_shape()[1]
            
            # Run forward pass to calculate embeddings
            print('Calculating features for images')
            nrof_images = len(faces)
            emb_array = np.zeros((nrof_images, embedding_size))
            feed_dict = { images_placeholder:faces, phase_train_placeholder:False }
            emb_array = sess.run(embeddings, feed_dict=feed_dict)

    return (det_arr,emb_array)
    
