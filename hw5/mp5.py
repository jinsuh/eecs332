import numpy as np
import scipy.signal
from scipy import ndimage
from PIL import Image

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
    image_array = image_array.astype('int32')
    dx = ndimage.sobel(image_array, 0)
    dy = ndimage.sobel(image_array, 1) 
    theta = np.arctan2(dy.astype(float), dx.astype(float))
    theta *= 255.0
    mag = np.hypot(dx, dy)
    mag *= 255.0 / np.max(mag)
    scipy.misc.imsave('sobel_result.jpg', theta)
    return mag, theta

im_arr = build_image_array("lena.bmp")
new_arr = gaussian_smoothing(im_arr, 3, 3)
gradient(new_arr)

# array = new_arr.astype(np.uint8)
# image = Image.fromarray(array)
# image.save('result.bmp', 'bmp')
