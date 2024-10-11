import cv2
import numpy as np


def laplacian_contrast_weight(img: np.ndarray):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return np.abs(cv2.Laplacian(img_gray, cv2.CV_32F, ksize=3))


def saliency_weight(img: np.ndarray):
    return img


def saturation_weight(img: np.ndarray):
    return img


def weights_merged(img: np.ndarray):
    """
    In Ancuti et al., Input 1 and 2's weight maps are derived
    from the merge of their respective Laplacian, Saliency and
    Saturation weights.

    :param img:
    :return:
    """
    return img
