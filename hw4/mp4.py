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

def get_histogram(image_data, hist_dict, color_type):
	width, height = image_data.size
	for row in range(height):
		for col in range(width):
			r,g,b = image_data.getpixel((col, row))
			if color_type == 0:
				x,y,z = (math.floor(r/255.*10), math.floor(g/255.*10), math.floor(b/255.*10))
			elif color_type == 1:
				x,y,z = colorsys.rgb_to_hsv(math.floor(r/255.*10), math.floor(g/255.*10), math.floor(b/255.*10))
			else:
				s = r+g+b
				x = math.floor(r / float(s) * 100)
				y = math.floor(g / float(s) * 100)
				z = math.floor(b / float(s) * 100)
			if not (x,y) in hist_dict:
				hist_dict[(x,y)] = 1
			else:
				hist_dict[(x,y)] += 1
	return hist_dict

def train(image_paths, color_type):
	hist_dict = {}
	for image_path in image_paths:
		training_image = read_image(image_path)
		hsv_dict = get_histogram(training_image, hist_dict, color_type)

	return hsv_dict

def normalize_histogram_sum(hist):
	total = 0
	for value in hist.values():
		total += value
	print total
	for key in hist.keys():
		hist[key] /= float(total)
	return hist

def normalize_histogram_area(hist):
	area = np.trapz(hist.values())
	print area
	for key in hist:
		hist[key] = hist[key] / area
	return hist

def print_histogram(hist, name):
	plt.bar(range(len(hist)), hist.values())
	plt.title(name)
	plt.savefig(name)
	plt.clf()

def color_segmentation(image_data, threshold, color_type):
	image_paths = []
	for i in range(1, 12):
		image_path = 'training_images_2/sample_' + str(i) + '.jpg'
		image_paths.append(image_path)

	hsv_dict = train(image_paths, color_type)
	normalized_hsv_dict = normalize_histogram_sum(hsv_dict)
	print_histogram(normalized_hsv_dict, 'area_hist_sum')

	width, height = image_data.size
	new_image = [[0 for x in xrange(width)] for x in xrange(height)]

	for row in range(height):
		for col in range(width):
			r,g,b = image_data.getpixel((col, row))
			if color_type == 0:
				x,y,z = (math.floor(r/255.*10), math.floor(g/255.*10), math.floor(b/255.*10))
			elif color_type == 1:
				x,y,z = colorsys.rgb_to_hsv(math.floor(r/255.*10), math.floor(g/255.*10), math.floor(b/255.*10))
			else:
				s = r+g+b
				x = math.floor(r / float(s) * 100)
				y = math.floor(g / float(s) * 100)
				z = math.floor(b / float(s) * 100)
			if (x,y) in normalized_hsv_dict and normalized_hsv_dict[(x,y)] > threshold:
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
	color_type = float(sys.argv[3])
	image = read_image(image_path)
	width, height = image.size
	image_array = color_segmentation(image, threshold, color_type)
	create_result_image(image_array, 'result_' + image_path.replace('.bmp', ''))

if __name__ == "__main__":
    main()
