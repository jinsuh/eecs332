from PIL import Image

def connected_component_labeling(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	width, height = image_data.size

	labels = []
	label_count = 1
	error_table = []

	for row in range(height):
		labels.append([])
		for col in range(width):
			pixel = image_data.getpixel((col, row))

			if pixel == 255:
				labels[row].append(0)
			else:
				up = label_up(row, col, labels)
				left = label_left(row, col, labels)

				if up == left and up != 0 and left != 0:
					labels[row].append(up)
				elif up != left and (up == 0 or left == 0):
					labels[row].append(max(up, left))
				elif up != left and up > 0 and left > 0:
					label = min(up, left)
					labels[row].append(label)
					error_table[max(up, left) - 1] = label
				else:
					labels[row].append(label_count)
					error_table.append(label_count)
					label_count = label_count + 1
	return labels, error_table

def label_up(row, col, labels):
	if row - 1 < 0:
		return 0
	else:
		return labels[row - 1][col]

def label_left(row, col, labels):
	if col - 1 < 0:
		return 0
	else:
		return labels[row][col - 1]

def correct_error_labels(error_table, label):
	if label == 0:
		return 0
	elif error_table[label - 1] == label:
		return label
	else:
		return correct_error_labels(error_table, error_table[label - 1])

def correct_labels(labels, error_table):
	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			labels[row][col] = correct_error_labels(error_table, labels[row][col])
	return labels

labels, error_table = connected_component_labeling('test.bmp')
corrected_labels = correct_labels(labels, error_table)
for row in corrected_labels:
	print row