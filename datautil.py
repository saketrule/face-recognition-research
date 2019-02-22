from face import Face 
from Image import Image
import cv2
import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
## For encoding image
import base64
from PIL import Image as pImage
from io import BytesIO
'''
Data format:
np array of Images with faces
'''
name_map = {
0:'ayush jain',
1: 'vidya rodge',
2: 'ayush garg',
3: 'shubham sangle',
4: 'vaishali',
5: 'rohit',
6: 'reena',
7: 'vishal',
8: 'priyansh',
9: 'shradha',
10: 'agastya',
11: 'pratik',
12: 'prashanth',
13: 'nitish',
14: 'sathwik',
15: 'sai krupa',
16: 'madhav',
17: 'k sandeep',
18: 'sharan',
19: 'ayush kumar',
20: 'ramya',
21: 'sandeep',
22: 'pravalika',
23: 'bhoomik',
24: 'nikhil',
25: 'varshini',
26: 'shashank',
27: 'merwin',
28: 'atharva',
29: 'prudhvi',
30: 'pranav',
-1: 'unknown'
}

class DataUtil:
    def readFaceData(self,path):
        with open(path,'rb') as f:
            images = pickle.load(f)
        return images

    def writeFaceData(self,images,path,filename):
        with open(path+'/'+filename+'.pickle','wb') as f:
            pickle.dump(images,f)

    def saveImages(self,images,path):
        if(not os.path.exists(path)):
            os.mkdir(path)
        for ind,image in enumerate(images):
            cv2.imwrite(path+'/img{}.png'.format(ind),image)

    def encodeImage(self,image,xScale=0.4,yScale=0.4):
        low_image = cv2.resize(image,(0,0),fx=xScale,fy=yScale)
        pil_img = pImage.fromarray(low_image)
        buff = BytesIO()
        pil_img.save(buff, format="JPEG")
        enc_image = base64.b64encode(buff.getvalue()).decode("utf-8")
        print('[getImage] Type of image {} '.format(type(image)))
        return enc_image    

    # Input - ndarray of image
    def labelFaces(self,image):
        img = image.getImage().copy()
        for i,face in enumerate(image.faces):
            x1,y2,x2,y1 = face.bound_box
            cv2.rectangle(img, (y1,x1), (y2,x2), (0, 0, 255), 5)
            if face.label is not None:
                cv2.putText(img,'{} : {} ({})'.format(i,face.label,name_map[int(face.label)]),(y1,x2),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
        return img

    def labelFaces2(self,image):
        img = image.getImage().copy()
        for i,face in enumerate(image.faces):
            x1,y2,x2,y1 = face.bound_box
            cv2.rectangle(img, (y1,x1), (y2,x2), (0, 0, 255), 5)
            if face.label is not None:
		cv2.putText(img,face.label,(y1,x2),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
                #cv2.putText(img,'{}% {}'.format(face.confidence,name_map[int(face.label)]),(y1,x2),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            
        return img


    # Input - Image object
    def showImage(self,image,showFaces=False):
        plt.ion()
        plt.figure(figsize = (20, 10))
        if(showFaces):
            plt.imshow(self.labelFaces2(image))
        else:
            plt.imshow(image.getImage())
        plt.show()

        
    def getDataFromFolder(self,path):
        files = os.listdir(path)
        data = []
        for file in files:
            if (file[0]!='.'):
                newImage = Image()
                newImage.path = path
                newImage.fileName = file
                data.append(newImage)
        return np.array(data)

    def readOldData(self,path,sourcePath):
        with open(path,'rb') as f:
            oldData = pickle.load(f)
        images,faces = oldData['images'],oldData['faces']
        data , facedata = dict(), dict()
        for img in images:
            imageObject = Image()
            imageObject.fileName = img[0]
            imageObject.path = sourcePath
            #imageObject.image = img[1]
            data[img[0]] = imageObject
        for face in faces:
            if (face.img_name not in facedata):
                facedata[face.img_name] = []
            facedata[face.img_name].append(face)
        for img_name in facedata:
            data[img_name].faces = np.array(facedata[img_name])
        return np.array([data[key] for key in data])

    def readImages(self, image_dir):
        images = []
        img_names = os.listdir(image_dir)
        for name in img_names:
            newImage = Image()
            newImage.path = image_dir
            newImage.fileName = name
            images.append(newImage)
        return np.array(images)

    def getFileNames(self, path):
        return np.array([x for x in os.listdir(path) if x[0]!='.'])

    def filterImagesFromFolder(self,folderPath,data):
        fileNames = self.getFileNames(folderPath)
        return np.array([img for img in data if img.fileName in fileNames])

    # To get faces from folder, stored by name {img_name}_{face_index}.jpg
    def getFacesFromFolder(self,folderPath,data,bin_label):
        fileNames = self.getFileNames(folderPath)
        faces = []
        for file in fileNames:
            comp = file.split('_')
            img_name,face_index = comp[0]+'_'+comp[1],int(comp[2][:-4])
            image = [img for img in data if (img.fileName == img_name)]
            #print(img_name,face_index,img.fileName)
            assert(len(image)==1)
            image[0].faces[face_index].label = bin_label
            faces.append((image[0],face_index))
        return faces

    def getFacesFromFolder2(self,folderPath,data,bin_label):
        fileNames = self.getFileNames(folderPath)
        faces = []
        for file in fileNames:
            comp = file.split('$')
            img_name, face_index = comp[0], int(comp[1][:-4])
            image = [img for img in data if (img.fileName == img_name)]
            assert(len(image)==1)
            image[0].faces[face_index].label = bin_label
            faces.append((image[0],face_index))
        return faces


    def getTruthFromFolder(self,truth_path,data,n_bins):
        bins = [self.getFacesFromFolder(truth_path+'/bin{}'.format(n),data,n) for n in range(n_bins)]
        faces,X,Y = [],[],[]
        for binn in bins:
            for img,face_id in binn:
                face = img.faces[face_id]
                faces.append(face)
                X.append(face.enc)
                Y.append(face.label)
        return bins,faces,X,Y

    def getTruthFromFolder2(self,truth_path,data):
        fileNames = self.getFileNames(truth_path)
        bins = [self.getFacesFromFolder2(truth_path + '/' + filename, data, filename) for filename in fileNames]
        faces,X,Y = [],[],[]
        for binn in bins:
            for img,face_id in binn:
                face = img.faces[face_id]
                faces.append(face)
                X.append(face.enc)
                Y.append(face.label)
        return bins,faces,X,Y
    
    def getEncodingConstraintStrings(self,data):
        datastring = ''
        constraintstring = ''
        i=0
        for image in data:
            if (image.faces is None):
                continue
            for face in image.faces:
                encoding=' '.join(map(str,face.enc)) + "\n"
                datastring += encoding
            for j in range(i,i+len(image.faces)):
                for k in range(j+1,i+len(image.faces)):
                    constraintstring += "{} {} -1\n".format(j,k)
            i += len(image.faces)
        return datastring,constraintstring

    def getDataLabels(self,data):
        labels,encodings = [],[]
        for image in data:
            for face in image.faces:
                encodings.append(face.enc)
                labels.append(face.label)
        return encodings,labels

    def writeBins(self, bins, direc = '../../Data/GROUND_TRUTH'):
        BIN_PATH = direc
        if(not os.path.isdir(BIN_PATH)):
            os.mkdir(BIN_PATH)
        for i, b in enumerate(bins):
            BIN_DIR = BIN_PATH + '/bin' + str(i)
            if(not os.path.isdir(BIN_DIR)):
                os.mkdir(BIN_DIR)
            for f in b:
                FACE_PATH = BIN_DIR + '/' + f.img_name + '$' + str(f.indexInImage) + '.jpg'
                print(FACE_PATH)
                cv2.imwrite(FACE_PATH, f.myFace)        
        
######## Convert old computed data to new format
#a = DataUtil()
#data1 = a.readOldData('./Data/old_pickles/tosave.p','./Data/Session1')
#data2 = a.readOldData('./Data/old_pickles/tosave2.p','./Data/Session1')
#data3 = a.readOldData('./Data/old_pickles/tosave3.p','./Data/Session2')
#data = np.append(data1,data2)
#a.writeFaceData(data,'./Data/pickles','session1.pickle')
#a.writeFaceData(data3,'./Data/pickles','session2.pickle')
#a.showImage(data[0])
#a.showImage(data3[0])
