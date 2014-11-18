import numpy as np
import scipy.signal
from scipy import ndimage
from PIL import Image
import math
import matplotlib.pyplot as plt
import sys

# NEIGHBORS = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]

def buildImageArray(imagePath):
    image = Image.open(imagePath)
    imageData = image.getdata()
    width, height = imageData.size
    imageArray = [[0 for x in xrange(width)] for x in xrange(height)]
    for row in range(height):
        for col in range(width):
            imageArray[row][col] = imageData.getpixel((col, row))
    return imageArray

def print_histogram(hist, name):
    plt.bar(range(len(hist)), hist.values())
    plt.title(name)
    plt.savefig(name)
    plt.clf()

def hough_transform(image):
    width = len(image[0])
    height = len(image)
    H = {}
    max_value = 0
    max_r = 0
    for row in range(height):
        for col in range(width):
            if image[row][col] == 255:
                for t in range(0, 180):
                    theta = t * math.pi / 180
                    r = int(math.cos(theta) * col + math.cos(theta) * row)
                    if r > max_r:
                        max_r = r
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

    print max_r + math.sqrt(height * height + width * width)
    newArr = [[0 for x in xrange(int(max_r + math.sqrt(height * height + width * width)) + 1)] for x in xrange(181)]
    for key in H:
        # H[key] /= max_value
        y = int(key[0] + math.sqrt(height * height + width * width)) #row
        x = key[1] #theta
        print y
        # print 2 * math.sqrt(height * height + width * width)
        # print key
        # print H[key]
        newArr[x][y] = H[key]
    array = np.array(newArr).astype(np.uint8)
    image = Image.fromarray(array)
    image.save('param_result.bmp', 'bmp')

    # print_histogram(H, 'hough_transform_hist') 
    # print max_value
    # print max_keys
    
    # plt.plot(rs, theta)
    # plt.show()


# sys.setrecursionlimit(100000)

# imageArray = buildImageArray("test.bmp")
# newArray = gaussianSmoothing(imageArray, 1, 1)
# mag, theta = gradient(newArray)
# mag = nonMaximaSuppression(mag, theta)
# tLow, tHigh = findThreshold(mag, 0.9)
# tLowMag = create_threshold_mag(mag, tLow)
# tHighMag = create_threshold_mag(mag, tHigh)

# image = newImage = [[0 for x in xrange(len(tLowMag[0]))] for x in xrange(len(tLowMag))]
# edge_linking(tLowMag, tHighMag, image)
image = buildImageArray("result_test.bmp")
hough_transform(image)
# array = np.array(image).astype(np.uint8)
# image = Image.fromarray(array)
# image.save('result_test.bmp', 'bmp')
