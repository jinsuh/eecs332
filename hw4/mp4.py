from PIL import Image
import numpy as np
import colorsys
import matplotlib.pyplot as plt
import math
import sys

def read_image(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	return image_data

def get_HSV_histogram(image_data, hsv_dict):
	width, height = image_data.size
	for row in range(height):
		for col in range(width):
			r,g,b = image_data.getpixel((col, row))
			h,s,v = colorsys.rgb_to_hsv(math.floor(r/255.*10), math.floor(g/255.*10), math.floor(b/255.*10))
			if not (h,s) in hsv_dict:
				hsv_dict[(h,s)] = 1
			else:
				hsv_dict[(h,s)] += 1
	return hsv_dict

def train(image_paths):
	hsv_dict = {}
	for image_path in image_paths:
		training_image = read_image(image_path)
		hsv_dict = get_HSV_histogram(training_image, hsv_dict)

	return hsv_dict

def normalize_histogram_sum(hist):
	total = 0
	for key in hist.keys():
		total += hist[key]
	for key in hist.keys():
		hist[key] /= float(total)
	return hist

def normalize_histogram_area(hist):
	y = [0 for x in range(len(hist))]
	count = 0
	for key in hist:
		y[count] = hist[key]
		count += 1
	area = np.trapz(y)
	for key in hist:
		hist[key] = hist[key] / area
	return hist

def print_histogram(hist, name):
	hist_array_y = [0 for x in range(len(hist.keys()))]
	count = 0
	for key in hist.keys():
		hist_array_y[count] = hist[key]
		count += 1
	plt.bar(range(len(hist_array_y)), hist_array_y)
	plt.title(name)
	plt.savefig(name)
	plt.clf()

def color_segmentation(image_data, threshold):
	image_paths = []
	for i in range(1, 12):
		image_path = 'training_images_2/sample_' + str(i) + '.jpg'
		image_paths.append(image_path)

	hsv_dict = train(image_paths)
	normalized_hsv_dict = normalize_histogram_sum(hsv_dict)
	print_histogram(normalized_hsv_dict, 'area_hist')

	width, height = image_data.size
	new_image = [[0 for x in xrange(width)] for x in xrange(height)]

	for row in range(height):
		for col in range(width):
			r,g,b = image_data.getpixel((col, row))
			h,s,v = colorsys.rgb_to_hsv(math.floor(r/255.*10), math.floor(g/255.*10), math.floor(b/255.*10))
			if (h,s) in normalized_hsv_dict and normalized_hsv_dict[(h,s)] > threshold:
				new_image[row][col] = (r,g,b)
			else:
				new_image[row][col] = (0,0,0)

	return new_image

def create_result_image(image_array, name):
	array = (np.array(image_array)).astype(np.uint8)
	image = Image.fromarray(array)
	image.save(name + '.bmp', 'bmp')

def main():
	image_path = sys.argv[1]
	threshold = float(sys.argv[2])
	image = read_image(image_path)
	width, height = image.size
	image_array = color_segmentation(image, threshold)
	create_result_image(image_array, 'result_' + image_path.replace('.bmp', ''))

if __name__ == "__main__":
    main()
