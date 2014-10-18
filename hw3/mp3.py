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

def probabilityMassFunction(histogram_data, size):
	for i in range(len(histogram_data)):
		value = histogram_data[i]
		histogram_data[i] = value / size

	return histogram_data


