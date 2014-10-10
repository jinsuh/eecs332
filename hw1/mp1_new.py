from PIL import Image
# import numpy as np

def connected_component_labeling(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	width, height = image_data.size

	labels = []
	label_count = 1
	error_table = {}

	for row in range(height):
		labels.append([])
		for col in range(width):
			pixel = image_data.getpixel((col, row))

			if pixel == 0:
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
					
					if up in error_table:
						error_table[left] = error_table[up]
					elif left in error_table:
						error_table[up] = error_table[left]
					else:
						error_table[max(up, left)] = label
				else:
					labels[row].append(label_count)
					error_table[label_count] = label_count
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

def correct_error_table(error_table, label, correct_label):
	print 'correct', correct_label
	print 'label', label
	print 'error', error_table[label]
	print 'type correct', type(error_table[label])
	print 'type error', type(label)
	print 'equal', (error_table[label] == label)
	if error_table[label] == label:
		error_table[label] = correct_label
		return error_table
	else:
		return correct_error_table(error_table, error_table[label], correct_label)

def correct_error_label(error_table, label):
	if error_table[label] == label:
		return label
	else:
		return correct_error_label(error_table, error_table[label])

def correct_labels(labels, error_table):
	label_count = 1
	label_map = {}
	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			if labels[row][col] > 0:
				label = correct_error_label(error_table, labels[row][col])

				if not label in label_map:
					label_map[label] = label_count
					label_count = label_count + 1

				labels[row][col] = label_map[label]
	return labels, label_count - 1

def ccl(image_path):
	labels, error_table = connected_component_labeling(image_path)
	corrected_labels, label_count = correct_labels(labels, error_table)
	return corrected_labels, label_count

# labels, num = ccl('face.bmp')
# image_array = (np.array(labels) * 255 / 6).astype(np.uint8)
# image = Image.fromarray(image_array)
# image.save('result.bmp', 'bmp')