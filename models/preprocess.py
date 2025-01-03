import os
import base64
from pathlib import Path
from typing import Union
import requests
import numpy as np
import cv2

def histogram_equalization(image):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply histogram equalization
        equalized_image = cv2.equalizeHist(gray)
        # Convert back to color
        return cv2.cvtColor(equalized_image, cv2.COLOR_GRAY2BGR)

def adjust_contrast(image, alpha=1.5, beta=0):
        # Apply contrast adjustment
        contrast_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return contrast_image
    
def denoise_image(image):
    # Apply non-local means denoising
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


def enhance_image(image):
        # Apply histogram equalization
        image = histogram_equalization(image)
        # Adjust the contrast
        image = adjust_contrast(image)
        # Denoise the image
        image = denoise_image(image)
        return image

# def get_image(img_uri: Union[str, np.ndarray]) -> np.ndarray:
#     """
#     Load the given image
#     Args:
#         img_path (str or numpy array): exact image path, pre-loaded numpy array (BGR format)
#             , base64 encoded string and urls are welcome
#     Returns:
#         image itself
#     """
#     # if it is pre-loaded numpy array
#     if isinstance(img_uri, np.ndarray):  # Use given NumPy array
#         img = img_uri.copy()

#     # if it is base64 encoded string
#     elif isinstance(img_uri, str) and img_uri.startswith("data:image/"):
#         img = load_base64_img(img_uri)

#     # if it is an external url
#     elif isinstance(img_uri, str) and img_uri.startswith("http"):
#         img = load_image_from_web(url=img_uri)

#     # then it has to be a path on filesystem
#     elif isinstance(img_uri, (str, Path)):
#         if isinstance(img_uri, Path):
#             img_uri = str(img_uri)

#         if not os.path.isfile(img_uri):
#             raise ValueError(f"Input image file path ({img_uri}) does not exist.")

#         # pylint: disable=no-member
#         img = cv2.imread(img_uri)

#     else:
#         raise ValueError(
#             f"Invalid image input - {img_uri}."
#             "Exact paths, pre-loaded numpy arrays, base64 encoded "
#             "strings and urls are welcome."
#         )

#     # Validate image shape
#     if len(img.shape) != 3 or np.prod(img.shape) == 0:
#         raise ValueError("Input image needs to have 3 channels at must not be empty.")

#     return img


def get_image(img_path):
    if isinstance(img_path, str):
        if not os.path.exists(img_path):
            raise ValueError(f"Path does not exist: {img_path}")
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Failed to load image: {img_path}")
    elif isinstance(img_path, np.ndarray):
        img = img_path.copy()
    else:
        raise ValueError("Invalid input type - expected str or np.ndarray")
        
    if img.ndim == 2:  # grayscale
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.ndim == 3 and img.shape[2] == 4:  # RGBA
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif img.ndim == 3 and img.shape[2] == 3:  # BGR or RGB
        pass  # No conversion needed
    else:
        raise ValueError(f"Unexpected image format: shape={img.shape}")
        
    return img


def load_base64_img(uri) -> np.ndarray:
    """Load image from base64 string.

    Args:
        uri: a base64 string.

    Returns:
        numpy array: the loaded image.
    """
    encoded_data = uri.split(",")[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return img_bgr


def load_image_from_web(url: str) -> np.ndarray:
    """
    Loading an image from web
    Args:
        url: link for the image
    Returns:
        img (np.ndarray): equivalent to pre-loaded image from opencv (BGR format)
    """
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    image_array = np.asarray(bytearray(response.raw.read()), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


def resize_image(img: np.ndarray, scales: list, allow_upscaling: bool) -> tuple:
    """
    Args:
        img (numpy array): given image
        scales (list)
        allow_upscaling (bool)
    Returns
        resized image, im_scale
    """
    img_h, img_w = img.shape[0:2]
    target_size = scales[0]
    max_size = scales[1]

    if img_w > img_h:
        im_size_min, im_size_max = img_h, img_w
    else:
        im_size_min, im_size_max = img_w, img_h

    im_scale = target_size / float(im_size_min)
    if not allow_upscaling:
        im_scale = min(1.0, im_scale)

    if np.round(im_scale * im_size_max) > max_size:
        im_scale = max_size / float(im_size_max)

    if im_scale != 1.0:
        img = cv2.resize(img, None, None, fx=im_scale, fy=im_scale, interpolation=cv2.INTER_LINEAR)

    return img, im_scale


def preprocess_image(img: np.ndarray, allow_upscaling: bool) -> tuple:
    """
    Args:
        img (numpy array): given image
        allow_upscaling (bool)
    Returns:
        tensor, image shape, im_scale
    """
    pixel_means = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    pixel_stds = np.array([1.0, 1.0, 1.0], dtype=np.float32)
    pixel_scale = float(1.0)
    scales = [1024, 1980]

    img, im_scale = resize_image(img, scales, allow_upscaling)
    img = img.astype(np.float32)
    im_tensor = np.zeros((1, img.shape[0], img.shape[1], img.shape[2]), dtype=np.float32)

    # Make image scaling + BGR2RGB conversion + transpose (N,H,W,C) to (N,C,H,W)
    for i in range(3):
        im_tensor[0, :, :, i] = (img[:, :, 2 - i] / pixel_scale - pixel_means[2 - i]) / pixel_stds[
            2 - i
        ]

    return im_tensor, img.shape[0:2], im_scale
