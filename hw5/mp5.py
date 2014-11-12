import numpy as np
import scipy.signal
from scipy import ndimage
from PIL import Image
import math
import matplotlib.pyplot as plt
import sys

NEIGHBORS = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]

def gauss2D(shape=(3,3),sigma=0.5):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h

def gaussian_smoothing(image_array, N, sigma):
    g_mask = gauss2D((N, N), sigma)
    new_im_arr = scipy.signal.convolve2d(image_array, g_mask, mode = 'same')
    return new_im_arr

def build_image_array(image_path):
    image = Image.open(image_path)
    image_data = image.getdata()
    width, height = image_data.size
    image_array = [[0 for x in xrange(width)] for x in xrange(height)]
    for row in range(height):
        for col in range(width):
            image_array[row][col] = image_data.getpixel((col, row))[0]
    return image_array

def gradient(image_array):
    # image_array = image_array.astype(float)
    dx = ndimage.sobel(image_array, 0)
    dy = ndimage.sobel(image_array, 1) 
    theta = np.arctan2(dy.astype(float), dx.astype(float))
    theta *= 180 / math.pi
    for i in range(len(theta)):
        for j in range(len(theta[i])):
            if theta[i][j] < 0:
                theta[i][j] += 360

    print theta

    mag = np.hypot(dx, dy)
    mag *= 255.0 / np.max(mag)
    scipy.misc.imsave('sobel_result.jpg', theta)
    return mag, theta

def non_maxima_surpression(mag, theta):
    #new (dx, dy)
    lut = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
    for i in range(len(mag)):
        for j in range(len(mag[i])):
            index = int(round((theta[i][j]/45.0))) % 7 + 2
            # print index
            neighbor = lut[index]
            neighbor2 = tuple([x * -1 for x in neighbor])
            # print 'engihbor', neighbor
            # print 'neighbor 22222', neighbor2
            # print i, j
            # print i,j
            # print len(mag)
            # print len(mag[i])
            if ((j + neighbor[0]) < 0) or ((j + neighbor[0]) >= len(mag[i])) or ((i + neighbor[1]) < 0) or (i + neighbor[1] >= len(mag)) :
                neighbor_grad = -999999999999
            else:
                neighbor_grad = mag[i + neighbor[1]][j + neighbor[0]]



            # print j + neighbor2[0]
            # print i + neighbor2[1]
            if ((j + neighbor2[0]) < 0) or ((j + neighbor2[0]) >= len(mag[i])) or ((i + neighbor2[1]) < 0) or (i + neighbor2[1] >= len(mag)):
                neighbor2_grad = -999999999999
            else:
                neighbor2_grad = mag[i + neighbor2[1]][j + neighbor2[0]]

            if (neighbor_grad > mag[i][j]) or (neighbor2_grad > mag[i][j]):
                mag[i][j] = 0
    scipy.misc.imsave('suppress_result_or.jpg', mag)
    return mag

def find_threshold(mag, per):
    d = {}
    for i in range(len(mag)):
        for j in range(len(mag[i])):
            val = int(round(mag[i][j] / 255.00 * 100))
            if val not in d:
                d[val] = 1
            else:
                d[val] += 1

    cummulative_sum = 0
    printHistogram(d, 'hist')
    for key in d:
        cummulative_sum += d[key]

        if cummulative_sum > len(mag) * len(mag[0]) * per:
            temp = key
            break
    t_high = temp / (100.0) #bin size - 1
    t_low = t_high * .5
    return t_low, t_high

def printHistogram(hist, name):
    plt.bar(range(len(hist)), hist.values())
    plt.title(name)
    plt.savefig(name)
    plt.clf()

def create_thresh_mag(mag, thresh):
    new_image = [[0 for x in xrange(len(mag[0]))] for x in xrange(len(mag))]
    for i in range(len(mag)):
        for j in range(len(mag[i])):
            val = mag[i][j] / 255.0
            if (val > thresh):
                new_image[i][j] = 255
            else:
                new_image[i][j] = 0
    array = np.array(new_image).astype(np.uint8)
    image = Image.fromarray(array)
    image.save('thresh' + str(thresh) + '.bmp', 'bmp')
    return new_image

def edge_linking(t_low_mag, t_high_mag, image):
    for i in range(len(t_high_mag)):
        for j in range(len(mag[i])):
            if t_high_mag[i][j] != 0 and image[i][j] == 0:
                recursive_t_high(i, j, t_high_mag, t_low_mag, image)

def recursive_t_high(x, y, t_high_mag, t_low_mag, image):
    neighbors = get_neighbors(x, y, image)
    for neighbor in neighbors:
        if t_high_mag[neighbor[0]][neighbor[1]] == 0:
            image[neighbor[0]][neighbor[1]] = 1
        else:
            image[neighbor[0]][neighbor[1]] = 255
        if end_point(neighbor[0], neighbor[1], x, y, t_high_mag):
            recursive_t_low(neighbor[0], neighbor[1], t_high_mag, t_low_mag, image)
            return
        else:
            recursive_t_high(neighbor[0], neighbor[1], t_high_mag, t_low_mag, image)

def recursive_t_low(x, y, t_high_mag, t_low_mag, image):
    neighbors = get_neighbors(x, y, image)
    for neighbor in neighbors:
        if t_low_mag[neighbor[0]][neighbor[1]] == 0:
            image[neighbor[0]][neighbor[1]] = 1
        else:
            image[neighbor[0]][neighbor[1]] = 255
        if end_point(neighbor[0], neighbor[1], x, y, t_low_mag) or t_high_mag[neighbor[0]][neighbor[1]]:
            return
        else:
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

def end_point(x, y, xprev, yprev, mag): #False -> endpoint
    width = len(mag[0])
    height = len(mag)
    if (check_neighbor_bound(x - 1, y - 1, width, height)): #lower left
        if (mag[x-1][y-1] != 0 and (xprev != x-1 or yprev != y-1)):
            return (x-1, y-1)
    if (check_neighbor_bound(x, y - 1, width, height)): #bottom
        if (mag[x][y-1] != 0 and (xprev != x or yprev != y-1)):
            return (x, y-1)
    if (check_neighbor_bound(x + 1, y - 1, width, height)): #lower right
        if (mag[x+1][y-1] != 0 and (xprev != x+1 or yprev != y-1)):
            return (x+1, y-1)
    if (check_neighbor_bound(x + 1, y, width, height)): #right
        if (mag[x+1][y] != 0 and (xprev != x+1 or yprev != y)):
            return (x+1, y)
    if (check_neighbor_bound(x + 1, y + 1, width, height)): #upper right
        if (mag[x+1][y+1] != 0 and (xprev != x+1 or yprev != y+1)):
            return (x+1, y+1)
    if (check_neighbor_bound(x, y + 1, width, height)): #top
        if (mag[x][y+1] != 0 and (xprev != x or yprev != y+1)):
            return (x, y+1)
    if (check_neighbor_bound(x - 1, y + 1, width, height)): #upper left
        if (mag[x-1][y+1] != 0 and (xprev != x-1 or yprev != y+1)):
            return (x-1, y+1)
    if (check_neighbor_bound(x - 1, y, width, height)): #left
        if (mag[x-1][y] != 0 and (xprev != x-1 or yprev != y)):
            return (x-1, y)
    return False


def check_neighbor_bound(x, y, width, height):
    return (x >= 0 and x < width) or (y >= 0 and y < height)

sys.setrecursionlimit(2000)

im_arr = build_image_array("lena.bmp")
new_arr = gaussian_smoothing(im_arr, 3, 3)
mag, theta = gradient(new_arr)
# print np.array(mag).max()
mag = non_maxima_surpression(mag, theta)
t_low, t_high = find_threshold(mag, 0.91)
t_low_mag = create_thresh_mag(mag, t_low)
t_high_mag = create_thresh_mag(mag, t_high)
image = new_image = [[0 for x in xrange(len(t_low_mag[0]))] for x in xrange(len(t_low_mag))]
edge_linking(t_low_mag, t_high_mag, image)
# array = new_arr.astype(np.uint8)
# image = Image.fromarray(array)
# image.save('result.bmp', 'bmp')
