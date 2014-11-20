import numpy as np
import scipy.signal
from scipy import ndimage
from PIL import Image
import math
import matplotlib.pyplot as plt
import sys
import cv2

NEIGHBORS = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]

def gauss2D(N = 3, sigma=0.5):
    x, y = np.mgrid[-N//2 + 1:N//2 + 1, -N//2 + 1:N//2 + 1]
    g = np.exp(-((x**2 + y**2)/(2.0*sigma**2)))
    return g/g.sum()

def gaussianSmoothing(imageArray, N, sigma):
    gMask = gauss2D(N, sigma)
    newImageArray = scipy.signal.convolve2d(imageArray, gMask, mode = 'same', boundary = 'symm')
    array = np.array(newImageArray).astype(np.uint8)
    image = Image.fromarray(array)
    return newImageArray

def buildImageArray(imagePath):
    image = Image.open(imagePath)
    imageData = image.getdata()
    width, height = imageData.size
    imageArray = [[0 for x in xrange(width)] for x in xrange(height)]
    for row in range(height):
        for col in range(width):
            imageArray[row][col] = imageData.getpixel((col, row))[0]
    return imageArray

def gradient(imageArray):
    dy = ndimage.sobel(imageArray, 0)
    dx = ndimage.sobel(imageArray, 1)
    dx *= -1
    theta = np.arctan2(dy.astype(float), dx.astype(float))
    theta *= 180 / math.pi
    for i in range(len(theta)):
        for j in range(len(theta[i])):
            if theta[i][j] < 0:
                theta[i][j] += 360
    
    mag = np.hypot(dx, dy)
    return mag, theta

def nonMaximaSuppression(mag, theta):
    lut = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
    for i in range(len(mag)):
        for j in range(len(mag[i])):
            index = int(round((theta[i][j]/45.0))) % 7 + 2
            neighborA = lut[index]
            neighborB = tuple([x * -1 for x in neighborA])
            if ((i + neighborA[0]) < 0) or ((i + neighborA[0]) >= len(mag)) or ((j + neighborA[1]) < 0) or (j + neighborA[1] >= len(mag[i])) :
                neighborAGradient = -999999999999
            else:
                neighborAGradient = mag[i + neighborA[0]][j + neighborA[1]]

            if ((i + neighborB[0]) < 0) or ((i + neighborB[0]) >= len(mag)) or ((j + neighborB[1]) < 0) or (j + neighborB[1] >= len(mag[i])):
                neighborBGradient = -999999999999
            else:
                neighborBGradient = mag[i + neighborB[0]][j + neighborB[1]]

            if (neighborAGradient >= mag[i][j]) or (neighborBGradient >= mag[i][j]):
                mag[i][j] = 0
    # scipy.misc.imsave('suppress_result_or.jpg', mag)
    return mag

def findThreshold(mag, per):
    d = {}
    for i in range(len(mag)):
        for j in range(len(mag[i])):
            val = int(round(mag[i][j] / 255.00 * 100))
            if val not in d:
                d[val] = 1
            else:
                d[val] += 1

    cummulativeSum = 0
    print_histogram(d, 'hist')
    for key in d:
        cummulativeSum += d[key]

        if cummulativeSum > len(mag) * len(mag[0]) * per:
            temp = key
            break
    tHigh = temp / (100.0) #bin size - 1
    tLow = tHigh * .5
    return tLow, tHigh

def print_histogram(hist, name):
    plt.bar(range(len(hist)), hist.values())
    plt.title(name)
    plt.savefig(name)
    plt.clf()

def create_threshold_mag(mag, thresh):
    newImage = [[0 for x in xrange(len(mag[0]))] for x in xrange(len(mag))]
    for i in range(len(mag)):
        for j in range(len(mag[i])):
            val = mag[i][j] / 255.0
            if (val > thresh):
                newImage[i][j] = 255
            else:
                newImage[i][j] = 0
    array = np.array(newImage).astype(np.uint8)
    image = Image.fromarray(array)
    image.save('thresh' + str(thresh) + '.bmp', 'bmp')
    return newImage

def edge_linking(t_low_mag, t_high_mag, image):
    for i in range(len(t_high_mag)):
        for j in range(len(t_high_mag[i])):
            if t_high_mag[i][j] != 0 and image[i][j] == 0:
                image[i][j] == 255
                recursive_t_high(i, j, t_high_mag, t_low_mag, image)
    return image

def recursive_t_high(row, col, t_high_mag, t_low_mag, image):
    neighbors = get_neighbors(row, col, image)
    for neighbor in neighbors:
        # print "row, col high: " + str(row), str(col)
        if image[neighbor[0]][neighbor[1]] == 0:
            if t_high_mag[neighbor[0]][neighbor[1]] != 0:
                image[neighbor[0]][neighbor[1]] = 255
            else:
                image[neighbor[0]][neighbor[1]] = 1
            if end_point(neighbor[0], neighbor[1], t_high_mag):
                if t_low_mag[neighbor[0]][neighbor[1]] != 0:
                    # print "recurse low"
                    recursive_t_low(neighbor[0], neighbor[1], t_high_mag, t_low_mag, image)
                else:
                #     # print "return"
                    return
            else:
                # print "recurse high"
                recursive_t_high(neighbor[0], neighbor[1], t_high_mag, t_low_mag, image)
        # else:
        #     return

def recursive_t_low(row, col, t_high_mag, t_low_mag, image):
    neighbors = get_neighbors(row, col, image)
    for neighbor in neighbors:
        # print "row, col: " + str(row), str(col)
        if t_high_mag[neighbor[0]][neighbor[1]] != 0:
            image[neighbor[0]][neighbor[1]] = 255
            break
        elif t_low_mag[neighbor[0]][neighbor[1]] != 0:
            neighbor_check = get_neighbors_exist(neighbor[0], neighbor[1], image)
            check = False
            for neighbor_exist in neighbor_check:
                if image[neighbor_exist[0]][neighbor_exist[1]] == 255:
                    image[neighbor[0]][neighbor[1]] = 255
                    check = True
            if not check:
                image[neighbor[0]][neighbor[1]] = 1    
        else:
            image[neighbor[0]][neighbor[1]] = 1
        if end_point(neighbor[0], neighbor[1], t_low_mag) or t_high_mag[neighbor[0]][neighbor[1]] != 0:
            # print "return"
            return
        else:
            # print "again"
            recursive_t_low(neighbor[0], neighbor[1], t_high_mag, t_low_mag, image)


def in_bounds(row, col, width, height):
    return row >= 0 and row < height and col >= 0 and col < width

def get_neighbors(row, col, image):
    neighbors = []
    for neighbor in NEIGHBORS:
        neighbor_row = row + neighbor[0]
        neighbor_col = col + neighbor[1]
        if in_bounds(neighbor_row, neighbor_col, len(image[0]), len(image)) and image[neighbor_row][neighbor_col] == 0:
            neighbors.append((neighbor_row, neighbor_col))
    return neighbors

def get_all_neighbors(row, col, image):
    neighbors = []
    for neighbor in NEIGHBORS:
        neighbor_row = row + neighbor[0]
        neighbor_col = col + neighbor[1]
        if in_bounds(neighbor_row, neighbor_col, len(image[0]), len(image)):
            neighbors.append((neighbor_row, neighbor_col))
    return neighbors    

def get_neighbors_exist(row, col, image):
    neighbors = []
    for neighbor in NEIGHBORS:
        neighbor_row = row + neighbor[0]
        neighbor_col = col + neighbor[1]
        if in_bounds(neighbor_row, neighbor_col, len(image[0]), len(image)) and image[neighbor_row][neighbor_col] != 0:
            neighbors.append((neighbor_row, neighbor_col))
    return neighbors


def end_point(row, col, mag): #True -> endpoint
    width = len(mag[0])
    height = len(mag)

    neighbors = get_all_neighbors(row, col, mag)
    count = 0
    for neighbor in neighbors:
        neighbor_row = neighbor[0]
        neighbor_col = neighbor[1]

        if mag[neighbor_row][neighbor_col] != 0 and neighbor_row != row and neighbor_col != col:
            return False
    # if count == 1:
    #     return True
    # else:
    #     return False
    return True

def check_neighbor_bound(x, y, width, height):
    return (x >= 0 and x < width) and (y >= 0 and y < height)

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
        for col in range(height):
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
# imageArray = buildImageArray("input.bmp")
# newArray = gaussianSmoothing(imageArray, 3, 3)
# mag, theta = gradient(newArray)
# mag = nonMaximaSuppression(mag, theta)
# tLow, tHigh = findThreshold(mag, 0.96)
# tLowMag = create_threshold_mag(mag, tLow)
# tHighMag = create_threshold_mag(mag, tHigh)

# image = newImage = [[0 for x in xrange(len(tLowMag[0]))] for x in xrange(len(tLowMag))]
# image = edge_linking(tLowMag, tHighMag, image)
# array = np.array(image).astype(np.uint8)
# image = Image.fromarray(array)
# image.save('edge_result.bmp', 'bmp')
img = cv2.imread('input.bmp',0)
edges = cv2.Canny(img,80,100)

hough_transform(edges, 1, 0.5)
# draw_line(edges, 136, 59)
array = np.array(edges).astype(np.uint8)
image = Image.fromarray(array)
image.save('result_test.bmp', 'bmp')
