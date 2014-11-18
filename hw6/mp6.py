import numpy as np
import scipy.signal
from scipy import ndimage
from PIL import Image
import math
import matplotlib.pyplot as plt
import sys

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

def hough_transform(image):
    width = len(image[0])
    height = len(image)
    H = {}
    max_value = 0

    for row in range(height):
        for col in range(width):
            if image[row][col] == 255:
                for t in range(0, 180):
                    theta = t * math.pi / 180
                    r = math.cos(theta) * col + math.cos(theta) * row
                    key = (r, t)

                    if key in H:
                        H[key] += 1
                    else:
                        H[key] = 1

                    if H[key] > max_value:
                        max_value = H[key]
    
    max_keys = []
    thetas = []
    rs = []
    for key in H:
        thetas.append(key[1])
        rs.append(key[0])
        if H[key] == max_value:
            max_keys.append(key)

    print_histogram(H, 'hough_transform_hist')
    print max_value
    print max_keys
    
    plt.plot(rs, theta)
    plt.show()


sys.setrecursionlimit(100000)

imageArray = buildImageArray("test.bmp")
newArray = gaussianSmoothing(imageArray, 1, 1)
mag, theta = gradient(newArray)
mag = nonMaximaSuppression(mag, theta)
tLow, tHigh = findThreshold(mag, 0.9)
tLowMag = create_threshold_mag(mag, tLow)
tHighMag = create_threshold_mag(mag, tHigh)

image = newImage = [[0 for x in xrange(len(tLowMag[0]))] for x in xrange(len(tLowMag))]
edge_linking(tLowMag, tHighMag, image)
hough_transform(image)
# array = np.array(image).astype(np.uint8)
# image = Image.fromarray(array)
# image.save('result_test.bmp', 'bmp')