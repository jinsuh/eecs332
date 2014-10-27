from PIL import Image
import numpy as np

def read_image(imagePath):
	image = Image.open(imagePath)
	image_data = image.getdata()

	return image_data

def histogram(image_data):
	width, height = image_data.size
	histogram = [0 for x in range(256)]
	for row in range(height):
		for col in range(width):
			pixel = image_data.getpixel((col, row))
			rgb_average = (pixel[0] + pixel[1] + pixel[2]) / 3
			histogram[rgb_average] = histogram[rgb_average] + 1
	return histogram

def probability_mass_function(histogram_data, size):
	for i in range(len(histogram_data)):
		value = histogram_data[i]
		histogram_data[i] = value / float(size)

	return histogram_data

def cumulative_distributive_function(histogram_data):
	for i in range(len(histogram_data)):
		value = histogram_data[i]

		if i > 0:
			histogram_data[i] = histogram_data[i] + histogram_data[i - 1]

	return histogram_data 

def histogram_equalization(image_data):
	width, height = image_data.size
	histogram_data = histogram(image_data)
	histogram_data = probability_mass_function(histogram_data, width * height)
	histogram_data = cumulative_distributive_function(histogram_data)
	image = [[0 for x in xrange(width)] for x in xrange(height)]
	for row in range(height):
		for col in range(width):
			pixel = image_data.getpixel((col, row))
			rgb_average = (pixel[0] + pixel[1] + pixel[2]) / 3
			image[row][col] = histogram_data[rgb_average] * 256

	return image

def create_result_image(imageArray, name):
	array = (np.array(imageArray)).astype(np.uint8)
	image = Image.fromarray(array)
	image.save(name + '.bmp', 'bmp')

#test code
image = read_image('moon.bmp')
new_image = histogram_equalization(image)
create_result_image(new_image, 'moon_result2')