import numpy as np
from Image import Image
from face import Face
import sys
sys.path.append('./classifier')
from classifier.classifier import get_faces

class Detector:
	def detect_embedd(self, images):
		faces = []
		for ind, image in enumerate(images):
			print("Detecting faces in image {}/{}".format(ind+1,len(images)))
			newFaces = []
			det_arr, emb_arr = get_faces(image)
			for fl, enc in zip(det_arr, emb_arr):
				face = Face()
				face.img_name = img.fileName
				face.enc = emb_arr
				x0, x1, x2, x3 = fl
				face.bound_box = (x1,x2,x3,x0)
				face.myFace = img.getImage()[x1:x3,x0:x2]
				newFaces.append(face)
			image.faces = np.array(newFaces)
			faces += newFaces
		return faces	