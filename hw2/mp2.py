from PIL import Image
import numpy as np

def read_image(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	return image_data

def erosion(image, structure_element):
	width, height = image.size

	finArr = [[0 for x in xrange(width)] for x in xrange(height)]
	flattened_elements= flatten_structure_element(structure_element)
	for row in range(height):
		for col in range(width):
			pixel = image.getpixel((col, row))
			if pixel != 0:
				isZero = False
				for tup in flattened_elements:
					#check bounds
					if (inBounds(row, col, tup, width, height)):
						if image.getpixel((col + tup[1], row + tup[0]))[0] == 255:
							isZero = True
							finArr[row][col] = 0
							break
				if (not isZero):
					finArr[row][col] = 1
	return finArr

def inBounds(row, col, tup, width, height):
	return col+tup[1] >= 0 and row+tup[0] >= 0 and col+tup[1] < width and row+tup[0] < height


def dilation(image, structure_element):
	pass

def opening(image, structure_element):
	pass

def closing(image, structure_element):
	pass

def boundary(image):
	pass

def flatten_structure_element(structure_element):
	center = len(structure_element) / 2
	flattened_structure_element = []

	for row in range(len(structure_element)):
		for col in range(len(structure_element[row])):
			if structure_element[row][col] == 1:
				flattened_structure_element.append((row - center, col - center))

	return flattened_structure_element


image = read_image('test_erosion.bmp')
structure_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
# print flatten_structure_element(structure_element)
finalArr = erosion(image, structure_element)
# print finalArr
numpyArr = (np.array(finalArr) * 255).astype(np.uint8)
im = Image.fromarray(numpyArr)
im.save('result_test.bmp')