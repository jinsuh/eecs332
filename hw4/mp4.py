from PIL import Image
import numpy as np
import colorsys
import matplotlib.pyplot as plt

def read_image(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	return image_data

def get_HSV_histogram(image_data, width, height):
	hsv_dict = dict()
	for row in range(height):
		for col in range(width):
			r,g,b = image_data.getpixel((col, row))
			h,s,v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
			if not (h,s) in hsv_dict:
				hsv_dict[(h,s)] = 1
			else:
				hsv_dict[(h,s)] += 1
	return hsv_dict

def normalize_histogram_area(hist):
	total = 0
	for key in hist.keys():
		total += hist[key]
	for key in hist.keys():
		hist[key] /= total
	return hist

def print_histogram(hist):
	hist_array_y = [0 for x in range(len(hist.keys()))]
	count = 0
	for key in hist.keys():
		hist_array_y[count] = hist[key]
		count += 1
	plt.bar(range(len(hist_array_y)), hist_array_y)
	plt.title('HSV Histogram')
	plt.savefig('HSV Histogram')
	plt.clf()

def create_result_image(image_array, name):
	array = (np.array(image_array)).astype(np.uint8)
	image = Image.fromarray(array)
	image.save(name + '.bmp', 'bmp')

#test code
image = read_image('gun.bmp')
width, height = image.size
hsv_dict = get_HSV_histogram(image, width, height)
print_histogram(hsv_dict)