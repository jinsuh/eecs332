from PIL import Image
import numpy as np

def pass1(image):
	image = Image.open(image)
	imageData = image.getdata()
	width, height = imageData.size

	labels = []
	labelCount = 1
	errorTable = {}

	for row in range(height):
		labels.append([])
		for col in range(width):
			pixel = imageData.getpixel((col, row))

			if pixel == 0:
				labels[row].append(0)
			else:
				up = labelUp(row, col, labels)
				left = labelLeft(row, col, labels)

				if up == left and up != 0 and left != 0:
					labels[row].append(up)
				elif up != left and (up == 0 or left == 0):
					labels[row].append(max(up, left))
				elif up != left and up > 0 and left > 0:
					label = min(up, left)
					labels[row].append(label)
					
					if up in errorTable:
						errorTable[left] = errorTable[up]
					else:
						errorTable[up] = errorTable[left]
				else:
					labels[row].append(labelCount)
					errorTable[labelCount] = labelCount
					labelCount += 1
	return labels, errorTable

def labelUp(row, col, labels):
	if row - 1 < 0:
		return 0
	else:
		return labels[row - 1][col]

def labelLeft(row, col, labels):
	if col - 1 < 0:
		return 0
	else:
		return labels[row][col - 1]

def correctLabel(errorTable, label):
	if errorTable[label] == label:
		return label
	else:
		return correctLabel(errorTable, errorTable[label])

def correctLabels(labels, errorTable):
	count = 0
	currLabel = {}
	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			if labels[row][col] > 0:
				correct = correctLabel(errorTable, labels[row][col])
				# print "correct", correct
				# print currLabel
				if not correct in currLabel:
					count += 1
					currLabel[correct] = count	
				labels[row][col] = currLabel[correct]
	return labels, count

def sizeFilter(labels, threshold):
	currLabel = {}
	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			l = labels[row][col]
			if not l in currLabel:
				currLabel[l] = 1
			else:
				currLabel[l] += 1
	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			l = labels[row][col]
			if l > 0:
				count = currLabel[l]
				if count < threshold:
					labels[row][col] = 0
	return labels

def ccl(image):
	labels, errorTable = pass1(image)
	correctedLabels, num = correctLabels(labels, errorTable)
	numpyArr = (np.array(correctedLabels) * 255 / 6).astype(np.uint8)
	im = Image.fromarray(numpyArr)
	labelDict = {}
	for row in correctedLabels:
		for col in row:
			labelDict[col] = True	
	im.save('result' + image, 'bmp')
	return correctedLabels, num

# Face
finLabels, num = ccl('face.bmp')
print num

# Test
finLabels, num = ccl('test.bmp')
print num

# Gun
finLabels, num = ccl('gun.bmp')
redoLabels= sizeFilter(finLabels, 500)
numpyArr = (np.array(redoLabels) * 255 / 6).astype(np.uint8)
im = Image.fromarray(numpyArr)
im.save('resultgun.bmp')
labelDict = {}
for row in redoLabels:
	for col in row:
		labelDict[col] = True
print labelDict.keys()