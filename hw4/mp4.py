from PIL import Image
import numpy as np

def read_image(imagePath):
	image = Image.open(imagePath)
	image_data = image.getdata()

	return image_data

def create_result_image(imageArray, name):
	array = (np.array(imageArray)).astype(np.uint8)
	image = Image.fromarray(array)
	image.save(name + '.bmp', 'bmp')

#test code
image = read_image('moon.bmp')