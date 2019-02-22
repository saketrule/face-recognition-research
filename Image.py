from face_recognition import load_image_file
class Image:
	faces = None
	image = None  # To be a np array
	fileName = None
	imageId = None
	path = None
	def getImage(self):
		if (self.image is None):
			self.image = load_image_file(self.path + '/' + self.fileName)
		return self.image

