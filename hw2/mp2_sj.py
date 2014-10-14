from PIL import Image
import numpy as np

def read_image(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	width, height = image_data.size

	image_array = [[0 for x in xrange(width)] for x in xrange(height)]

	for row in range(height):
		for col in range(width):
			image_array[row][col] = image_data.getpixel((col, row))[0]

	return image_array

def erosion(image, structure_element):
	height = len(image)
	width = len(image[0])

	finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	flattened_elements= flatten_structure_element(structure_element)
	for row in range(height):
		for col in range(width):
			pixel = image[row][col]
			if pixel != 0:
				isZero = False
				for tup in flattened_elements:
					#check bounds
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


def dilation(image, structure_element):
	height = len(image)
	width = len(image[0])

	finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	flattened_elements= flatten_structure_element(structure_element)
	for row in range(height):
		for col in range(width):
			pixel = image[row][col]
			if pixel == 0:
				isNotZero = False
				for tup in flattened_elements:
					#check bounds
					if (inBounds(row, col, tup, width, height)):
						if image[row + tup[0]][col + tup[1]] == 255:
							isNotZero = True
							finArr[row + tup[0]][col + tup[1]] = 255
							break
				if (not isNotZero):
					finArr[row][col] = 255
			else:
				finArr[row][col] = 255
	return finArr
	# width, height = image.size

	# finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	# flattened_elements= flatten_structure_element(structure_element)
	# for row in range(height):
	# 	for col in range(width):
	# 		pixel = image.getpixel((col, row))
	# 		if pixel != 0:
	# 			isZero = False
	# 			for tup in flattened_elements:
	# 				#check bounds
	# 				if (inBounds(row, col, tup, width, height)):
	# 					if image.getpixel((col + tup[1], row + tup[0]))[0] == 255:
	# 						isZero = True
	# 						finArr[row][col] = 1
	# 						break
	# 			if (not isZero):
	# 				finArr[row][col] = 0
	# return finArr

def opening(image, structure_element):
	eroded_array = erosion(image, structure_element)
	dilated_array = dilation(eroded_array, structure_element)
	return dilated_array

def closing(image, structure_element):
	dilated_array = dilation(image, structure_element)
	eroded_array = erosion(dilated_array, structure_element)
	return eroded_array

def boundary(image):
	height = len(image)
	width = len(image[0])

	structure_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
	erodedImage = erosion(image, structure_element)
	finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	for row in range(height):
		for col in range(width):
			if erodedImage[row][col] == 255 and image[row][col] == 0:
				finArr[row][col] = 0
			# finArr[row][col] = min(erodedImage[row][col], image[row][col])
	# finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	# flattened_elements= flatten_structure_element(structure_element)
	# for row in range(height):
	# 	for col in range(width):
	# 		pixel = image[row][col]
	# 		if pixel == 0:
	# 			isNotZero = False
	# 			for tup in flattened_elements:
	# 				#check bounds
	# 				if (inBounds(row, col, tup, width, height)):
	# 					if image[row + tup[0]][col + tup[1]] == 255:
	# 						isNotZero = True
	# 						image[row + tup[0]][col + tup[1]] = 255
	# 						break
	return finArr

def flatten_structure_element(structure_element):
	center = len(structure_element) / 2
	flattened_structure_element = []

	for row in range(len(structure_element)):
		for col in range(len(structure_element[row])):
			if structure_element[row][col] == 1:
				flattened_structure_element.append((row - center, col - center))

	return flattened_structure_element


image = read_image('test_erosion_2.bmp')
# print image
structure_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
# print flatten_structure_element(structure_element)
finalArr = boundary(image)
# print finalArr
numpyArr = (np.array(finalArr)).astype(np.uint8)
im = Image.fromarray(numpyArr)
im.save('result_closing.bmp')