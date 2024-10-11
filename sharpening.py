import cv2
import numpy as np
from scipy.ndimage.filters import median_filter


def norm_unsharp_mask(img: np.ndarray):
    """
    Normalized unsharp mask\n
    S = (I + N {I − G ∗ I}) / 2\n
    where\n
    - G ∗ I is the Gaussian-filtered image and\n
    - N is the linear normalization (histogram stretching) operator.

    :param img: image to process
    :return: S
    """

    gaussian_filtered = cv2.GaussianBlur(img, (5, 5), 0)
    difference = img - gaussian_filtered

    difference_yuv = cv2.cvtColor((255 * difference).astype(np.uint8), cv2.COLOR_BGR2YUV)
    # equalizeHist helyett stretching legyen
    # difference_yuv[:, :, 0] = cv2.equalizeHist(difference_yuv[:, :, 0])

    ###
    # STRETCHING

    constant = ((255 - 0) / (difference_yuv.max() - difference_yuv.min())).astype(np.uint8)
    img_stretched = difference_yuv * constant

    ###

    # lin_normalized = cv2.cvtColor(difference_yuv, cv2.COLOR_YUV2BGR).astype(np.float32) / 255

    lin_normalized = cv2.cvtColor(img_stretched, cv2.COLOR_YUV2BGR).astype(np.float32) / 255

    return (img + lin_normalized) / 2


def unsharp(image, sigma, strength):
    image_mf = median_filter(image, sigma)
    lap = cv2.Laplacian(image, cv2.CV_32F)
    sharp = cv2.subtract(image, (cv2.multiply(strength,lap)))
    print(sharp.dtype)


    return sharp


def unsharp_mask(img: np.ndarray, sigma, strength):
    img_copy = img.copy()

    for i in range(3):
        img_copy[:, :, i] = unsharp(img[:, :, i], sigma, strength)

    return img_copy
