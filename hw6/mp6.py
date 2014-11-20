import numpy as np
import scipy.signal
from scipy import ndimage
from PIL import Image
import math
import matplotlib.pyplot as plt
import sys
import cv2

NEIGHBORS = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]



def print_histogram(hist, name):
    plt.bar(range(len(hist)), hist.values())
    plt.title(name)
    plt.savefig(name)
    plt.clf()

def in_bounds(row, col, width, height):
    return row >= 0 and row < height and col >= 0 and col < width

def get_all_neighbors(row, col, image):
    neighbors = []
    for neighbor in NEIGHBORS:
        neighbor_row = row + neighbor[0]
        neighbor_col = col + neighbor[1]
        if in_bounds(neighbor_row, neighbor_col, len(image[0]), len(image)):
            neighbors.append((neighbor_row, neighbor_col))
    return neighbors    

def generate_accumulator(image, quant):
    width = len(image[0])
    height = len(image)
    H = {}

    for row in range(height):
        for col in range(width):
            # print row, col
            if image[row][col] == 255:
                thetas = []
                rs = []

                for t in np.arange(-90, 90, quant):
                    theta = t * math.pi / 180
                    r = int(math.cos(theta) * col + math.sin(theta) * row)
                    key = (r, t)

                    thetas.append(t)
                    rs.append(r)

                    if key in H:
                        H[key] += 1
                    else:
                        H[key] = 1
    return H

def param_space(hist, quant):
    min_key_value = float('inf')
    max_key_value = 0

    for key in hist:
        if key[0] < min_key_value:
            min_key_value = key[0]
        if key[0] > max_key_value:
            max_key_value = key[0]

    print min_key_value
    print max_key_value

    r_range = abs(min_key_value) + max_key_value + 1

    matrix = [[0 for x in xrange(r_range)] for x in xrange(int(181 / quant))]

    max_H = np.max(hist.values())

    for key in hist:
        matrix[int((key[1] + 90) / quant)][key[0] + abs(min_key_value)] = hist[key]
    return matrix, max_H, min_key_value

def significant_intersection(matrix, threshold, max_hist):
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if matrix[row][col] > threshold * max_hist:
                neighbors = get_all_neighbors(row, col, matrix)

                check = True

                for neighbor in neighbors:
                    neighbor_row = neighbor[0]
                    neighbor_col = neighbor[1]

                    if matrix[row][col] <= matrix[neighbor_row][neighbor_col]:
                        check = False

                if not check:
                    matrix[row][col] = 0
            else:
                matrix[row][col] = 0
    return matrix

def hough_transform(image, quant, threshold):
    H = generate_accumulator(image, quant)
    matrix, max_hist, min_key_value = param_space(H, quant)
    matrix = significant_intersection(matrix, threshold, max_hist)

    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if matrix[row][col] != 0:
                print col - abs(min_key_value), row * quant - 90
                draw_line(image, col - abs(min_key_value), row * quant - 90)


    array = np.array(image).astype(np.uint8)
    image = Image.fromarray(array)
    image.save('thresholded.bmp', 'bmp')

                    # for neigh in NEIGHBORS:
                    #     new_key = (r + neigh[0], t + neigh[1])
                    #     if new_key in H:
                    #         H[new_key] += 1
                    #     else:
                    #         H[new_key] = 1

                # plt.plot(rs, thetas, color='#000000', alpha=0.01)
    
    

    # array = np.array(matrix).astype(np.uint8)
    # image = Image.fromarray(array)
    # image.save('param_result.bmp', 'bmp')

    # image = read_image('param_result.bmp')
    # new_image = histogram_equalization(image)
    # array = np.array(new_image).astype(np.uint8)
    # image = Image.fromarray(array)
    # image.save('param_result_hist_equalized.bmp', 'bmp')

    # max_keys = []
    # # thetas = []
    # # rs = []
    # for key in H:
    #     thetas.append(key[1])
    #     rs.append(key[0])
    #     if H[key] == max_value:
    #         max_keys.append(key)

    # for key in H:
    #     max_keys = []
    #     thetas = []
    #     rs = []

    #     for i in range(0, 180):
    #         thetas.append(i)
    #         theta = i * math.pi / 180
    #         rs.append(int(math.cos(theta) * col + math.cos(theta) * row))

    #     plt.plot(rs, thetas)

    # plt.show()

    # print_histogram(H, 'hough_transform_hist')
    # print max_value
    # print max_keys

def draw_line(image, r, theta):
    width = len(image[0])
    height = len(image)
    theta = theta * math.pi / 180

    for row in range(height):
        for col in range(width):
            if r == int(col * math.cos(theta) + row * math.sin(theta)):
                image[row][col] = 255

def probability_mass_function(histogram_data, size):
    for i in range(len(histogram_data)):
        value = histogram_data[i]
        histogram_data[i] = value / float(size)

    return histogram_data

def cumulative_distributive_function(histogram_data):
    for i in range(len(histogram_data)):
        value = histogram_data[i]

        if i > 0:
            histogram_data[i] = histogram_data[i] + histogram_data[i - 1]

    return histogram_data 

def histogram_equalization(image_data):
    width, height = image_data.size
    histogram_data = histogram(image_data)
    histogram_data = probability_mass_function(histogram_data, width * height)
    histogram_data = cumulative_distributive_function(histogram_data)
    image = [[0 for x in xrange(width)] for x in xrange(height)]
    for row in range(height):
        for col in range(width):
            pixel = image_data.getpixel((col, row))
            image[row][col] = histogram_data[pixel] * 256

    return image

def histogram(image_data):
    width, height = image_data.size
    histogram = [0 for x in range(256)]
    for row in range(height):
        for col in range(width):
            pixel = image_data.getpixel((col, row))
            histogram[pixel] = histogram[pixel] + 1
    return histogram

def read_image(imagePath):
    image = Image.open(imagePath)
    image_data = image.getdata()

    return image_data
    
sys.setrecursionlimit(100000)

# Canny Edge Detector
img = cv2.imread('input.bmp',0)
edges = cv2.Canny(img,50,200)
hough_transform(edges, 1, 0.7)

# array = np.array(edges).astype(np.uint8)
# image = Image.fromarray(array)
# image.save('result_test.bmp', 'bmp')