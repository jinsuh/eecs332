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

def flatten_structure_element(structure_element):
	center = len(structure_element) / 2
	flattened_structure_element = []

	for row in range(len(structure_element)):
		for col in range(len(structure_element[row])):
			if structure_element[row][col] == 1:
				flattened_structure_element.append((row - center, col - center))

	return flattened_structure_element

image = read_image('gun.bmp')
structure_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
print flatten_structure_element(structure_element)
# erosion(image, structure_element)