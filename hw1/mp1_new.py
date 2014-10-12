from PIL import Image
import numpy as np

def connected_component_labeling(image_path):
	image = Image.open(image_path)
	image_data = image.getdata()
	width, height = image_data.size

	labels = []
	label_count = 1
	equivalence_table = {}

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
					
					if up in equivalence_table:
						equivalence_table[left] = equivalence_table[up]
					elif left in equivalence_table:
						equivalence_table[up] = equivalence_table[left]
				else:
					labels[row].append(label_count)
					equivalence_table[label_count] = label_count
					label_count = label_count + 1
	return labels, equivalence_table

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

def correct_equivalence_label(equivalence_table, label):
	if equivalence_table[label] == label:
		return label
	else:
		return correct_equivalence_label(equivalence_table, equivalence_table[label])

def correct_labels(labels, equivalence_table):
	label_count = 0
	label_map = {}
	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			if labels[row][col] > 0:
				label = correct_equivalence_label(equivalence_table, labels[row][col])

				if not label in label_map:
					label_count = label_count + 1
					label_map[label] = label_count

				labels[row][col] = label_map[label]
	return labels, label_count

def correct_labels_with_size_filter(labels, equivalence_table, threshold):
	label_count = 0
	label_map = {}
	label_count_map = {}
	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			if labels[row][col] > 0:
				label = correct_equivalence_label(equivalence_table, labels[row][col])

				if not label in label_map:
					label_count = label_count + 1
					label_map[label] = label_count
					label_count_map[label_map[label]] = 1

				label_count_map[label_map[label]] = label_count_map[label_map[label]] + 1
				labels[row][col] = label_map[label]

	num_components_map = {}
	num_components = 0

	for row in range(0, len(labels)):
		for col in range(0, len(labels[row])):
			if labels[row][col] != 0 and label_count_map[labels[row][col]] <= threshold:
				labels[row][col] = 0
			elif labels[row][col] != 0 and not labels[row][col] in num_components_map:
				num_components_map[labels[row][col]] = True
				num_components = num_components + 1

	return labels, num_components

def create_result_image(labels, name):
	image_array = (np.array(labels) * 255 / 6).astype(np.uint8)
	image = Image.fromarray(image_array)
	image.save(name + '.bmp', 'bmp')

def ccl(image_path):
	labels, equivalence_table = connected_component_labeling(image_path)
	corrected_labels, label_count = correct_labels(labels, equivalence_table)
	return corrected_labels, label_count

def ccl_size_filter(image_path, threshold):
	labels, equivalence_table = connected_component_labeling(image_path)
	corrected_labels, label_count = correct_labels_with_size_filter(labels, equivalence_table, threshold)
	return corrected_labels, label_count

labels, num = ccl('test.bmp')
create_result_image(labels, 'result_test')
print 'test.bmp' + ' ' + str(num)
labels, num = ccl_size_filter('gun.bmp', 300)
create_result_image(labels, 'result_gun')
print 'gun.bmp' + ' ' + str(num)
labels, num = ccl('face.bmp')
create_result_image(labels, 'result_face')
print 'face.bmp' + ' ' + str(num)
