import numpy as np
from PIL import Image
from scipy.signal import convolve2d


def image2features(image: Image.Image) -> np.ndarray:
    res = []
    array = np.array(image, dtype=float)
    res.append(array)

    array_hsv = __get_hsv(image)
    res.append(array_hsv)

    array_gray = __get_grey(image)
    res.append(array_gray)

    vertical= __get_vertical(array)
    res.append(vertical)

    horizontal = __get_horizontal(array)
    res.append(horizontal)

    convolved = __get_convolved(array_gray)
    res.append(convolved)

    array_sum = __get_sum(array)
    res.append(array_sum)
    features = np.concatenate(res, axis=2)
    return features


def __get_sum(array: np.ndarray) -> np.ndarray:
    h, w, *_ = array.shape
    array_sum = array.sum(axis=2).reshape((h, w, 1))
    return array_sum


def __get_convolved(array_gray: np.ndarray) -> np.ndarray:
    h, w, *_ = array_gray.shape
    n = 10
    mask = np.ones((n, n)) / n ** 2
    convolved = convolve2d(array_gray.reshape((h, w)), mask, 'same').astype(np.uint8).reshape((h, w, 1))
    return convolved


def __get_horizontal(array: np.ndarray) -> np.ndarray:
    h, w, c = array.shape
    horizontal = np.empty((h, w, c))
    for row in range(h):
        horizontal[row, :, :] = np.quantile(array[row, :, :], q=0.5)
    horizontal = horizontal - array
    return horizontal


def __get_vertical(array: np.ndarray) -> np.ndarray:
    h, w, c = array.shape
    vertical = np.empty((h, w, c))
    for col in range(w):
        vertical[:, col, :] = np.quantile(array[:, col, :], q=0.5)
    vertical = vertical - array
    return vertical


def __get_grey(image: Image.Image) -> np.ndarray:
    image_grey = image.convert("L")
    array_gray = np.array(image_grey)
    h, w, *_ = array_gray.shape
    return array_gray.reshape((h, w, 1))


def __get_hsv(image: Image.Image) -> np.ndarray:
    image_hsv = image.convert('HSV')
    array_hsv = np.array(image_hsv)
    return array_hsv
