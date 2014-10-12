from PIL import Image

def read_image(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	return image_data

def erosion(image, structure_element):
	width, height = image.size

	for row in range(height):
		for col in range(width):
			pixel = image.getpixel((col, row))

			

def dilation(image, structure_element):
	pass

def opening(image, structure_element):
	pass

def closing(image, structure_element):
	pass

def boundary(image):
	pass

def getNeighbors(row, col):
	pass

image = read_image('gun.bmp')
structure_element = ((0, 0, 1), (0, 1, 1), (0, 2, 1), (1, 0, 1), (1, 1, 1), (1, 2, 1), (2, 0, 1), (2, 1, 1), (2, 2, 1))
erosion(image, structure_element)