from PIL import Image
import numpy as np

def ccl(image):
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
					elif left in errorTable:
						errorTable[up] = errorTable[left]
					else:
						errorTable[max(up, left)] = label
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

def correctErrorTable(errorTable, label, correctLabel):
	print 'correct', correctLabel
	print 'label', label
	print 'error', errorTable[label]
	print 'type correct', type(errorTable[label])
	print 'type error', type(label)
	print 'equal', (errorTable[label] == label)
	if errorTable[label] == label:
		errorTable[label] = correctLabel
		return errorTable
	else:
		return correctErrorTable(errorTable, errorTable[label], correctLabel)

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
				print "correct", correct
				print currLabel
				if not correct in currLabel:
					count += 1
					currLabel[correct] = count	
				labels[row][col] = currLabel[correct]
	return labels

labels, errorTable = ccl('face.bmp')
correctedLabels = correctLabels(labels, errorTable)

numpyArr = (np.array(correctedLabels) * 255 / 6).astype(np.uint8)
im = Image.fromarray(numpyArr)
im.save('result.bmp', 'bmp')

# print errorTable

# for i in errorTable:
	# print i, errorTable[i]

labelDict = {}
for row in labels:
	# print row
	for col in row:
		labelDict[col] = True

print labelDict.keys()