import cv2
import numpy as np


def comp_for_channel(channel: str, img: np.ndarray, alpha=1):
    """
    I_rc(x) = I_r(x) + α * (¯I_g − ¯I_r) * (1 − I_r(x)) * I_g(x)

    :param channel:
    :param img:
    :param alpha:
    :return:
    """

    avg_b = np.mean(img[:, :, 0])
    avg_g = np.mean(img[:, :, 1])
    avg_r = np.mean(img[:, :, 2])

    res = img.copy()

    if channel == 'red' or channel == 'r':
        res[:, :, 2] = img[:, :, 2] + alpha * (avg_g - avg_r) * (1 - img[:, :, 2]) * img[:, :, 1]
    elif channel == 'blue' or channel == 'b':
        res[:, :, 0] = img[:, :, 0] + alpha * (avg_g - avg_b) * (1 - img[:, :, 0]) * img[:, :, 1]

    return res


def gray_world(img: np.ndarray):
    avg_b = np.mean(img[:, :, 0])
    avg_g = np.mean(img[:, :, 1])
    avg_r = np.mean(img[:, :, 2])

    alpha = avg_g / avg_r
    betha = avg_g / avg_b

    res = img.copy()

    res[:, :, 2] = res[:, :, 2] * alpha
    res[:, :, 0] = res[:, :, 0] * betha

    return res
