from PIL import Image
import numpy as np

def readImage(imagePath):
	image = Image.open(imagePath)
	imageData = image.getdata()

	return imageData

def histogram(imageData):
	width, height = imageData.size
	histogram = [0 for x in range(256)]
	for row in range(height):
		for col in range(width):
			pixel = imageData.getpixel((col, row))
			rgb_average = (pixel[0] + pixel[1] + pixel[2]) / 3
			histogram[rgb_average] = histogram[rgb_average] + 1
	return histogram

def probabilityMassFunction(histogramData, size):
	for i in range(len(histogramData)):
		value = histogramData[i]
		histogramData[i] = value / float(size)

	return histogramData

def cumulativeDistributiveFunction(histogramData):
	for i in range(len(histogramData)):
		value = histogramData[i]

		if i > 0:
			histogramData[i] = histogramData[i] + histogramData[i - 1]

	return histogramData 

def histogramEqualization(imageData, histogramData):
	width, height = imageData.size
	image = [[0 for x in xrange(height)] for x in xrange(width)]
	for row in range(height):
		for col in range(width):
			pixel = imageData.getpixel((col, row))
			rgb_average = (pixel[0] + pixel[1] + pixel[2]) / 3
			image[col][row] = histogramData[rgb_average] * 256

	return image

def createResultImage(imageArray, name):
	array = (np.array(imageArray)).astype(np.uint8)
	image = Image.fromarray(array)
	image.save(name + '.bmp', 'bmp')

#test code
image = readImage('moon.bmp')
width, height = image.size
histogramData = histogram(image)
histogramData = probabilityMassFunction(histogramData, width * height)
histogramData = cumulativeDistributiveFunction(histogramData)
newImage = histogramEqualization(image, histogramData)
createResultImage(newImage, 'moon_result')