from amcrest import AmcrestCamera
import time
import datetime
import os
from PIL import Image as PIL_Image
import io
from matplotlib import pyplot as plt
import cv2
import numpy as np
from Image import Image

img_no = 1
# image_dir = ''
camera = None
cam2 = None

def initializeCamera():
  global camera, cam2
  ip = '10.21.4.48'
  port = 80
  username = 'admin'
  password = 'AmcrestCamera'
  camera = AmcrestCamera(ip, port, username, password, retries_connection=5).camera
  cam2 = AmcrestCamera(ip,port,username, password,retries_connection=5).camera

# helper function
def snap():
    print('calling cam.snapshot')
    time.sleep(0.75)
    image = cam2.snapshot(0,timeout=50).data
    time.sleep(1)
    try:
        image = PIL_Image.open(io.BytesIO(image))
        return image
    except:
        print('Image could not be retrieved from Camera. Try reconnecting and then taking snap.')   
    return -1
        
# saves image to image_dir and returns image object     
def saveImage(image_dir='./today'):
    img = snap()
    if img == -1:
        img = np.ones((1200, 1900, 3))
    global img_no
    img_array = np.array(img)
    if image_dir!=None:
	image_path = image_dir + '/image' + str(img_no) + '.png'
    	print('saving {}'.format(image_path))

    	cv2.imwrite(image_path, cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)) 
    newImage = Image()
    newImage.path = image_dir
    newImage.fileName = 'image' + str(img_no) + '.png'
    img_no += 1
    return newImage

###############  For moving camera
#time units
t_s = 0.1
t_m = 0.5
t_l = 1
t_buf = 0.5

# helper functions
def moveLeft(sleep_time):
    time.sleep(t_buf)
    camera.move_left(action = "start", channel = 0, vertical_speed = 1)
    time.sleep(sleep_time)
    camera.move_left(action = "stop", channel = 0, vertical_speed = 1)
    time.sleep(t_buf)

def moveRight(sleep_time):
    time.sleep(t_buf)
    camera.move_right(action = "start", channel = 0, vertical_speed = 1)
    time.sleep(sleep_time)
    camera.move_right(action = "stop", channel = 0, vertical_speed = 1)
    time.sleep(t_buf)

def moveUp(sleep_time):
    time.sleep(t_buf)
    camera.move_up(action="start",channel=0, vertical_speed=1)
    time.sleep(sleep_time)
    camera.move_up(action="stop",channel=0,vertical_speed=1)
    time.sleep(t_buf)

def moveDown(sleep_time):
    time.sleep(t_buf)
    camera.move_down(action="start",channel=0, vertical_speed=1)
    time.sleep(sleep_time)
    camera.move_down(action="stop",channel=0,vertical_speed=1)
    time.sleep(t_buf)

def resetx():
    moveLeft(11)
    moveDown(2)
    zoomOut(2)

def zoomIn(sleep_time):
    time.sleep(t_buf)
    camera.zoom_in(action = "start", channel = 0)
    time.sleep(sleep_time)
    camera.zoom_in(action = "stop", channel = 0)
    time.sleep(t_buf)
    # camera.focus_far()

def zoomOut(sleep_time):
    time.sleep(t_buf)
    camera.zoom_out(action = "start", channel = 0)
    time.sleep(sleep_time)
    camera.zoom_out(action = "stop", channel = 0)
    time.sleep(t_buf)
    # camera.focus_near()


class Tour():
  #off = [3.6, 3.6, 3.8]
  #z = [0.3, 0.7, 0.2]
  #up = [0, 0.5, 0.1]
  #ts = [0.07, 0.07, 0.06]
  #rows = [7, 8, 7]
  off = [5,6]
  z = [0.5, 1.3]
  up = [0.5, 0.8]
  ts = [0.1,0.05]
  rows = [12,10]
  up.reverse()
  z.reverse()
  rows.reverse()
  ts.reverse()
  off.reverse()

  def __init__(self,cols):
    if cols==-1:
        cols = len(self.rows)
    self.ncol = cols
    self.crow = 0
    self.ccol = 0
    self.getPos(0)

  def getPos(self,ccol):
    print('Reset')
    resetx()
    print("Reset done")
    moveRight(self.off[ccol])
    moveUp(self.up[ccol])
    zoomIn(self.z[ccol])  
  

  def getNext(self):
      lastSnap = (self.ccol==(self.ncol-1) and self.crow==self.rows[self.ccol])
      if lastSnap:
        return False
      if (self.crow==self.rows[self.ccol]):
          self.crow = 0
          self.ccol += 1
          self.getPos(self.ccol)
      else:
        moveRight(self.ts[self.ccol])
      print("[Camera] [{}] [{}] getNext".format(self.ccol,self.crow))
      for i in range(5):
      	print 'Image ' + str(i)
      	saveImage('./today')
      self.crow += 1
      return True


initializeCamera()
# For testing, remove
#for i in range(2):
#	a = Tour(-1)
#	while a.getNext():
#  		pass
