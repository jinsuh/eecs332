from PIL import Image
import numpy as np

def readImage(imagePath):
	image = Image.open(imagePath)
	imageData = image.getdata()

	return imageData

def histogram(imageData):
	width, height = imageData.size
	hist = [0 for x in range(255)]
	for row in range(width):
		for col in range(height):
			pixel = imageData.get((col, row))
			hist[pixel] = hist[pixel] + 1
	return hist
