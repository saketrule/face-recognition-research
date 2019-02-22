import sys
sys.path.append('../libs')
from Image import Image
from face import Face
import face_recognition as fr
import numpy as np

class Detector:
    def __init__(self, model_name):
        self.model_name = model_name

    def detect(self, images):
        faces = []
        for ind, img in enumerate(images):
            print("Detecting faces in image {}/{}".format(ind+1,len(images)))
            newfaces = []
            fls = fr.face_locations(img.getImage(), model = self.model_name)
            encs = fr.face_encodings(img.getImage(), fls)
            for (fl, enc) in zip(fls, encs):
                face = Face()
                face.bound_box = fl
                face.img_name = img.fileName
                face.enc = enc
                tlx, tly, brx, bry = fl
                x1 = tlx
                x2 = brx
                y1 = bry
                y2 = tly
                face.myFace = img.image[x1:x2,y1:y2]
                newfaces.append(face)
            img.faces = np.array(newfaces)
            faces += newfaces
        return faces        


