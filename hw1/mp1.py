from PIL import Image
def label(image):
	jpgfile = Image.open(image)
	data = jpgfile.getdata()
	width, height = data.size
	print jpgfile.load()[0, 0]
label("face.bmp")