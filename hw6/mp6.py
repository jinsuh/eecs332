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
    printHistogram(d, 'hist')
    for key in d:
        cummulativeSum += d[key]

        if cummulativeSum > len(mag) * len(mag[0]) * per:
            temp = key
            break
    tHigh = temp / (100.0) #bin size - 1
    tLow = tHigh * .5
    return tLow, tHigh

def printHistogram(hist, name):
    plt.bar(range(len(hist)), hist.values())
    plt.title(name)
    plt.savefig(name)
    plt.clf()

def createThresholdMag(mag, thresh):
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

def edgeLinking(tLowMag, tHighMag, image):
    for i in range(len(tHighMag)):
        for j in range(len(tHighMag[i])):
            if tHighMag[i][j] != 0 and image[i][j] == 0:
                image[i][j] == 255
                recursiveTHigh(i, j, tHighMag, tLowMag, image)

def recursiveTHigh(row, col, tHighMag, tLowMag, image):
    neighbors = getNeighbors(row, col, image)
    for neighbor in neighbors:
        # print "row, col high: " + str(row), str(col)
        if tHighMag[neighbor[0]][neighbor[1]] != 0:
            image[neighbor[0]][neighbor[1]] = 255
        else:
            image[neighbor[0]][neighbor[1]] = 1
        if endPoint(neighbor[0], neighbor[1], tHighMag):
            if tLowMag[neighbor[0]][neighbor[1]] != 0:
                # print "recurse low"
                findTLow(neighbor[0], neighbor[1], tHighMag, tLowMag, image)
            else:
            #     # print "return"
                return
        else:
            # print "recurse high"
            recursiveTHigh(neighbor[0], neighbor[1], tHighMag, tLowMag, image)

def findTLow(row, col, tHighMag, tLowMag, image):
    neighbors = getNeighbors(row, col, image)
    for neighbor in neighbors:
        # print "row, col: " + str(row), str(col)
        if tHighMag[neighbor[0]][neighbor[1]] != 0:
            image[neighbor[0]][neighbor[1]] = 255
        elif tLowMag[neighbor[0]][neighbor[1]] != 0:
            NeighborCheck = getNeighborsExists(neighbor[0], neighbor[1], image)
            check = False
            for neighborExist in NeighborCheck:
                if image[neighborExist[0]][neighborExist[1]] == 255:
                    image[neighbor[0]][neighbor[1]] = 255
                    check = True
            if not check:
                image[neighbor[0]][neighbor[1]] = 1    
        else:
            image[neighbor[0]][neighbor[1]] = 1
        if endPoint(neighbor[0], neighbor[1], tLowMag) or tHighMag[neighbor[0]][neighbor[1]] != 0:
            # print "return"
            return
        else:
            # print "again"
            findTLow(neighbor[0], neighbor[1], tHighMag, tLowMag, image)


def inBounds(row, col, width, height):
    return row >= 0 and row < height and col >= 0 and col < width

def getNeighbors(row, col, image):
    neighbors = []
    for neighbor in NEIGHBORS:
        neighborRow = row + neighbor[0]
        neighborCol = col + neighbor[1]
        if inBounds(neighborRow, neighborCol, len(image[0]), len(image)) and image[neighborRow][neighborCol] == 0:
            neighbors.append((neighborRow, neighborCol))
    return neighbors

def getAllNeighbors(row, col, image):
    neighbors = []
    for neighbor in NEIGHBORS:
        neighborRow = row + neighbor[0]
        neighborCol = col + neighbor[1]
        if inBounds(neighborRow, neighborCol, len(image[0]), len(image)):
            neighbors.append((neighborRow, neighborCol))
    return neighbors    

def getNeighborsExists(row, col, image):
    neighbors = []
    for neighbor in NEIGHBORS:
        neighborRow = row + neighbor[0]
        neighborCol = col + neighbor[1]
        if inBounds(neighborRow, neighborCol, len(image[0]), len(image)) and image[neighborRow][neighborCol] != 0:
            neighbors.append((neighborRow, neighborCol))
    return neighbors


def endPoint(row, col, mag):
    width = len(mag[0])
    height = len(mag)

    neighbors = getAllNeighbors(row, col, mag)
    count = 0
    for neighbor in neighbors:
        neighborRow = neighbor[0]
        neighborCol = neighbor[1]

        if mag[neighborRow][neighborCol] != 0:
            count += 1
    if count == 1:
        return True
    else:
        return False

sys.setrecursionlimit(100000)

imageArray = buildImageArray("lena.bmp")
newArray = gaussianSmoothing(imageArray, 3, 3)
mag, theta = gradient(newArray)
mag = nonMaximaSuppression(mag, theta)
tLow, tHigh = findThreshold(mag, 0.9)
tLowMag = createThresholdMag(mag, tLow)
tHighMag = createThresholdMag(mag, tHigh)

image = newImage = [[0 for x in xrange(len(tLowMag[0]))] for x in xrange(len(tLowMag))]
edgeLinking(tLowMag, tHighMag, image)
array = np.array(image).astype(np.uint8)
image = Image.fromarray(array)
image.save('result_test.bmp', 'bmp')
