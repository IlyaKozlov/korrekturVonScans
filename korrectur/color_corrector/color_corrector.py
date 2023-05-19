import gzip
import os
import pickle
from copy import deepcopy
from typing import Optional

import numpy as np
from PIL import Image

from color_corrector.image_features import image2features


class ColorCorrector:

    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "white_classifier.pkl.gz")
        model_path = os.path.abspath(model_path)
        with gzip.open(model_path) as input_file:
            self.model = pickle.load(input_file)

    def handle_image(self, image: Image.Image) -> Image.Image:
        image_array = np.array(image)

        predictions = self._get_predictions(image)

        if (predictions == "white").mean() > 0.5:
            image_array = self._correct_image(image_array, predictions)
        image_out = Image.fromarray(image_array)
        return image_out

    def _correct_image(self, image_array: np.ndarray, predictions: np.ndarray) -> np.ndarray:
        array_copy = deepcopy(image_array)
        is_white = (predictions == "white")
        h, w, c = image_array.shape
        step = 25

        mean_prev = image_array[is_white].mean(axis=0)
        for col in range(0, h + step, step):
            for row in range(0, w, step):
                mean = self._get_mean(col=col, row=row, is_white=is_white, image_array=image_array)

                if mean is not None:
                    mean_prev, mean = mean, (0.75 * mean_prev + 0.25 * mean)
                mean = mean_prev
                window_small = array_copy[col: col + step, row: row + step, :]
                fixed = (window_small * 255.0 / mean)
                fixed[fixed > 255] = 255
                fixed = fixed.astype(np.uint8)
                window_small[:, :, :] = fixed
        return array_copy

    def _get_mean(self,
                  col: int,
                  row: int,
                  is_white: np.ndarray,
                  image_array: np.ndarray) -> Optional[np.ndarray]:
        width = 60
        height = 20
        h, w, _ = image_array.shape
        left = max(0, col - width // 2)
        right = min(col + width // 2, h)
        top = max(0, row - height // 2)
        bottom = min(row + height // 2, w)
        window = image_array[left: right, top: bottom, :]
        window_mask = is_white[left: right, top: bottom]
        if window_mask.mean() > 0.20:
            mean = window[window_mask].mean(axis=0)
            return mean
        return None

    def _get_predictions(self, image: Image.Image) -> np.ndarray:
        image_array_features = image2features(image)
        h, w, c_f = image_array_features.shape
        image_array_flat = image_array_features.reshape(h * w, c_f)
        predictions = self.model.predict(image_array_flat)
        predictions = predictions.reshape(h, w)
        return predictions
