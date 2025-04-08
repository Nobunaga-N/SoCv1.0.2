import cv2
import numpy as np
import logging
import os
from typing import Tuple, Optional, List, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class RecognitionBase(ABC):
    """Базовый класс для распознавания на изображениях."""

    def __init__(self, threshold: float = 0.8):
        """
        Инициализация базового класса распознавания.

        Args:
            threshold: Порог соответствия (0-1), где 1 - идеальное совпадение
        """
        self.threshold = threshold

    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения для распознавания.

        Args:
            image: Исходное изображение

        Returns:
            Обработанное изображение
        """
        pass

    def bytes_to_cv2_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Преобразует изображение из байтов в формат numpy array для OpenCV.

        Args:
            image_bytes: Изображение в виде байтов

        Returns:
            Изображение в формате numpy array
        """
        try:
            # Преобразуем байты в numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            # Декодируем изображение
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"Ошибка при преобразовании изображения из байтов: {e}")
            raise

    def save_debug_image(self, image: np.ndarray, file_name: str, folder: str = "debug_images") -> None:
        """
        Сохраняет изображение для отладки.

        Args:
            image: Изображение в формате numpy array
            file_name: Имя файла для сохранения
            folder: Папка для сохранения
        """
        try:
            # Создаем папку, если она не существует
            os.makedirs(folder, exist_ok=True)

            # Формируем путь к файлу
            file_path = os.path.join(folder, file_name)

            # Сохраняем изображение
            cv2.imwrite(file_path, image)
            logger.debug(f"Сохранено отладочное изображение: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении отладочного изображения: {e}")