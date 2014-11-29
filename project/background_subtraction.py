from PIL import Image
import scipy.misc
import numpy as np
import matplotlib.pyplot as plt
from eecs332_library import *

def read_image_data(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	return image

def generate_image_array(image_data):
	width, height = image_data.size

	image_array = [[0 for col in range(width)] for row in range(height)]

	for row in range(height):
		for col in range(width):
			pixel = image_data.getpixel((col, row))
			pixel = int((pixel[0] + pixel[1] + pixel[2]) / 3)
			image_array[row][col] = pixel

	return image_array

def generate_average_histogram(image_data, histogram):
	width, height = image_data.size

	for row in range(height):
		for col in range(width):
			pixel = image_data.getpixel((col, row))
			pixel = int((pixel[0] + pixel[1] + pixel[2]) / 3)

			key = (row, col)

			if key not in histogram:
				histogram[key] = {}

			if pixel in histogram[key]:
				histogram[key][pixel] += 1
			else:
				histogram[key][pixel] = 1

	return histogram

def print_histogram(histogram, name):
	plt.bar(range(len(histogram)), histogram.values())
	plt.title(name)
	plt.show()
	# plt.savefig(name)
	# plt.clf()			

def generate_difference_image(image_array, average_image_array):
	# print "taking difference of frames..."
	difference_image_array = np.subtract(average_image_array, image_array)

	# print "saving difference image..."
	# scipy.misc.imsave('difference image.jpg', difference_image_array)

	# print "smoothing difference image..."
	smooth_image_array = gaussian_smoothing(difference_image_array, 4, 4)
	# scipy.misc.imsave('smooth difference image.jpg', smooth_image_array)

	return smooth_image_array

def generate_binary_image(image_array, threshold):
	width = len(image_array[0])
	height = len(image_array)
	
	binary_image_array = [[0 for col in range(width)] for row in range(height)]
	
	min_pixel_value = np.min(image_array)

	for row in range(height):
		for col in range(width):
			if image_array[row][col] + np.abs(min_pixel_value) > threshold:
				binary_image_array[row][col] = 255
			else:
				binary_image_array[row][col] = 0

	return binary_image_array

def main():
	images_paths_numbers = [i * 10 for i in range(2, 20)]

	histogram = {}

	print "reading images..."

	# read in images and generate average histogram
	for number in images_paths_numbers:
		image_data = read_image_data('test_frames/frame_' + str(number) + '.bmp')
		width, height = image_data.size
		histogram = generate_average_histogram(image_data, histogram)

	print "building average image..."

	# build average image using histogram frequencies
	average_image_array = [[0 for col in range(width)] for row in range(height)]

	for row in range(height):
		for col in range(width):
			key = (row, col)

			max_pixel_frequency = 0
			max_pixel_value = 0

			for pixel in histogram[key]:
				frequency = histogram[key][pixel]

				if frequency > max_pixel_frequency:
					max_pixel_frequency = frequency
					max_pixel_value = pixel

			average_image_array[row][col] = max_pixel_value

	print "saving average image..."

	scipy.misc.imsave('average image.jpg', average_image_array)

	print "reading in frame..."

	for number in images_paths_numbers:
		print 'frame ' + str(number)
		frame_image_data = read_image_data('test_frames/frame_' + str(number) + '.bmp')
		frame_image_array = generate_image_array(frame_image_data)
		frame_difference_image_array = generate_difference_image(frame_image_array, average_image_array)
		frame_difference_binary_image_array = generate_binary_image(frame_difference_image_array, 200)
		scipy.misc.imsave('result_frames/binary_difference_image_' + str(number) + '.jpg', frame_difference_binary_image_array)
		structure_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
		frame_closed_image_array = opening(frame_difference_binary_image_array, structure_element)
		scipy.misc.imsave('result_frames/closed_difference_image_' + str(number) + '.jpg', frame_closed_image_array)

if __name__ == "__main__":
	main()