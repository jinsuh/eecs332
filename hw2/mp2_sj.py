from PIL import Image
import numpy as np

def readImage(imagePath):
	image = Image.open(imagePath)
	imageData = image.getdata()
	width, height = imageData.size

	imageArray = [[0 for x in xrange(width)] for x in xrange(height)]

	for row in range(height):
		for col in range(width):
			imageArray[row][col] = imageData.getpixel((col, row))

	return imageArray

def erosion(image, structureElement):
	height = len(image)
	width = len(image[0])

	finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	flattenedElements= flattenStructureElement(structureElement)
	for row in range(height):
		for col in range(width):
			pixel = image[row][col]
			if pixel != 0:
				isZero = False
				for tup in flattenedElements:
					if (inBounds(row, col, tup, width, height)):
						if image[row + tup[0]][col + tup[1]] == 0:
							isZero = True
							finArr[row][col] = 0
							break
				if (not isZero):
					finArr[row][col] = 255
	return finArr

def inBounds(row, col, tup, width, height):
	return col+tup[1] >= 0 and row+tup[0] >= 0 and col+tup[1] < width and row+tup[0] < height


def dilation(image, structureElement):
	height = len(image)
	width = len(image[0])

	finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	flattenedElements= flattenStructureElement(structureElement)
	for row in range(height):
		for col in range(width):
			pixel = image[row][col]
			if pixel == 0:
				isNotZero = False
				for tup in flattenedElements:
					if (inBounds(row, col, tup, width, height)):
						if image[row + tup[0]][col + tup[1]] == 255:
							isNotZero = True
							finArr[row + tup[0]][col + tup[1]] = 255
							break
				if (not isNotZero):
					finArr[row][col] = 0
			else:
				finArr[row][col] = 255
	return finArr
	
def opening(image, structureElement):
	erodedArray = erosion(image, structureElement)
	dilatedArray = dilation(erodedArray, structureElement)
	return dilatedArray

def closing(image, structureElement):
	dilatedArray = dilation(image, structureElement)
	erodedArray = erosion(dilatedArray, structureElement)
	return erodedArray

def boundary(image):
	height = len(image)
	width = len(image[0])

	structureElement = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
	erodedImage = erosion(image, structureElement)
	for row in range(height):
		for col in range(width):
			if erodedImage[row][col] == 255:
				image[row][col] = 0
	return image

def flattenStructureElement(structureElement):
	center = len(structureElement) / 2
	flattenedStructureElement = []

	for row in range(len(structureElement)):
		for col in range(len(structureElement[row])):
			if structureElement[row][col] == 1:
				flattenedStructureElement.append((row - center, col - center))

	return flattenedStructureElement


# TESTING

image = readImage('gun.bmp')
structureElement = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
finalArr = opening(image, structureElement)
numpyArr = (np.array(finalArr)).astype(np.uint8)
im = Image.fromarray(numpyArr)
im.save('resultOpeningGun3x3.bmp')