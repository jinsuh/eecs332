from PIL import Image
def label(image):
	jpgfile = Image.open(image)
	data = jpgfile.getdata()
	width, height = data.size
	labelArr = {}
	labelCount = 1
	errorTable = []
	# print width, height
	# print jpgfile.load()[0, 0]
	for i in range(width):
		strRow = ""
		for j in range(height):
			currLabel = 0
			pixel = data.getpixel((i,j))
			# print pixel
			if pixel == 255: #background
				labelArr[i, j] = 0
			else:
				pixelUp = labelUp(labelArr, i, j)
				pixelLeft = labelLeft(labelArr, i, j)
				if pixelUp == 0 and pixelLeft == 0:
					labelArr[i, j] = labelCount
					errorTable.append(labelCount)
					labelCount += 1
				elif pixelUp == 0 or pixelLeft == 0:
					labelArr[i, j] = max(pixelLeft, pixelUp)
				else:
					if pixelUp == pixelLeft:
						labelArr[i,j] = pixelUp
					else: #note in error table
						val = min(pixelUp, pixelLeft)
						print pixel
						labelArr[i, j] = val
						# errorTable[max(pixelUp, pixelLeft) - 1] = val
			strRow += " " + str(labelArr[i, j])
		# print strRow
	return labelArr, errorTable

def labelUp(labelArr, row, col):
	if (col - 1) < 0:
		return 0
	else:
		return labelArr[row, col - 1]

def labelLeft(labelArr, row, col):
	if (row - 1) < 0:
		return 0
	else:
		return labelArr[row - 1, col]

def correctLabel(errorTable, label):
	if (errorTable[label - 1] == label):
		return label
	else:
		return correctLabel(errorTable, errorTable[label] - 1)

def secondPass(label, errorTable):
	print errorTable
	# for (row, col) in label:
	# 	label[row, col] = correctLabel(errorTable, label[row, col])

	# return label

lArr, errorTable = label("face.bmp")
correctedArry = secondPass(lArr, errorTable)

maxLabels = 0;
for i in correctedArry:
	for j in correctedArry[i]:
		maxLabels = max(maxLabels, correctedArry[i, j])
print maxLabels
# print lArr