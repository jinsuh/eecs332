from PIL import Image
import numpy as np
import scipy.signal

def gauss_2d(N = 3, sigma=0.5):
	x, y = np.mgrid[-N//2 + 1:N//2 + 1, -N//2 + 1:N//2 + 1]
	g = np.exp(-((x**2 + y**2)/(2.0*sigma**2)))
	return g/g.sum()

def gaussian_smoothing(image_array, N, sigma):
	g_mask = gauss_2d(N, sigma)
	new_image_array = scipy.signal.convolve2d(image_array, g_mask, mode = 'same', boundary = 'symm')

	height = len(new_image_array)
	width = len(new_image_array[0])

	max_value = np.max(new_image_array)

	for row in range(height):
		for col in range(width):
			new_image_array[row][col] = 255 * new_image_array[row][col] / max_value

	return new_image_array

def erosion(image, structure_element):
	height = len(image)
	width = len(image[0])

	final_array = [[0 for x in xrange(width)] for x in xrange(height)]
	flattened_element= flatten_structure_element(structure_element)
	for row in range(height):
		for col in range(width):
			pixel = image[row][col]
			if pixel != 0:
				is_zero = False
				for tup in flattened_element:
					if (in_bounds(row, col, tup, width, height)):
						if image[row + tup[0]][col + tup[1]] == 0:
							is_zero = True
							final_array[row][col] = 0
							break
				if (not is_zero):
					final_array[row][col] = 255
	return final_array

def dilation(image, structure_element):
	height = len(image)
	width = len(image[0])

	final_array = [[0 for x in xrange(width)] for x in xrange(height)]
	flattened_element= flatten_structure_element(structure_element)
	for row in range(height):
		for col in range(width):
			pixel = image[row][col]
			if pixel == 0:
				is_not_zero = False
				for tup in flattened_element:
					if (in_bounds(row, col, tup, width, height)):
						if image[row + tup[0]][col + tup[1]] == 255:
							is_not_zero = True
							final_array[row][col] = 255
							break
				if (not is_not_zero):
					final_array[row][col] = 0
			else:
				final_array[row][col] = 255
	return final_array
	
def opening(image, structure_element):
	eroded_array = erosion(image, structure_element)
	dilated_array = dilation(eroded_array, structure_element)
	return dilated_array

def closing(image, structure_element):
	dilated_array = dilation(image, structure_element)
	eroded_array = erosion(dilated_array, structure_element)
	return eroded_array

def in_bounds(row, col, tup, width, height):
	return col+tup[1] >= 0 and row+tup[0] >= 0 and col+tup[1] < width and row+tup[0] < height

def flatten_structure_element(structure_element):
	center = len(structure_element) / 2
	flattened_structure_element = []

	for row in range(len(structure_element)):
		for col in range(len(structure_element[row])):
			if structure_element[row][col] == 1:
				flattened_structure_element.append((row - center, col - center))

	return flattened_structure_element

def draw_line(image, r, theta):
	width = len(image[0])
	height = len(image)
	theta = theta * np.pi / 180

	for row in range(height):
		for col in range(width):
			if r == int(col * np.cos(theta) + row * np.sin(theta)):
				image[row][col] = (128, 128, 128)

	return image

def read_image_data(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	return image

def generate_gray_scale_image_array(image_data):
	width, height = image_data.size

	image_array = [[0 for col in range(width)] for row in range(height)]

	for row in range(height):
		for col in range(width):
			pixel = image_data.getpixel((col, row))
			pixel = int((pixel[0] + pixel[1] + pixel[2]) / 3)
			image_array[row][col] = pixel

	return image_array

def generate_rgb_image_array(image_data):
	width, height = image_data.size

	image_array = [[0 for col in range(width)] for row in range(height)]

	for row in range(height):
		for col in range(width):
			pixel = image_data.getpixel((col, row))
			image_array[row][col] = pixel

	return image_array