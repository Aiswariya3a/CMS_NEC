from typing import Union
from abc import ABC, abstractmethod
import numpy as np
from ..utils import package_utils

tf_version = package_utils.get_tf_major_version()
if tf_version == 1:
    from keras.models import Model
else:
    from tensorflow.keras.models import Model

# pylint: disable=too-few-public-methods
class Demography(ABC):
    model: Model
    model_name: str

    @abstractmethod
    def predict(self, img: np.ndarray) -> Union[np.ndarray, np.float64]:
        pass
