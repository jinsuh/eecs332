from PIL import Image
import numpy as np

def readImage(imagePath):
	image = Image.open(imagePath)
	imageData = image.getdata()

	return imageData
