import cv2
import numpy as np


def create_gamma_lut(gamma):
    lut = np.arange(0, 256, 1, np.float32)
    lut = lut / 255.0
    lut = lut ** gamma
    lut = np.uint8(lut * 255.0)

    return lut


def gamma_correction(img: np.ndarray, gamma: float):
    res = cv2.LUT((255 * img).astype(np.uint8), create_gamma_lut(gamma))
    return res.astype(np.float32) / 255
