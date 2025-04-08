import cv2
import numpy as np
import pytesseract
import re
import logging
import os
from typing import List, Tuple, Optional, Dict, Any
from src.core.recognition.base import RecognitionBase

logger = logging.getLogger(__name__)


class TextRecognition(RecognitionBase):
    """Класс для распознавания текста на скриншотах игры."""

    def __init__(self, tessdata_path: Optional[str] = None, threshold: float = 0.6):
        """
        Инициализация объекта для распознавания текста.

        Args:
            tessdata_path: Путь к директории с данными Tesseract (если None, используется по умолчанию)
            threshold: Порог соответствия (0-1), где 1 - идеальное совпадение
        """
        super().__init__(threshold)
        self.tessdata_path = tessdata_path
        self._configure_tesseract()

    def _configure_tesseract(self) -> None:
        """Настраивает Tesseract OCR."""
        try:
            # Проверяем доступность pytesseract
            pytesseract.get_tesseract_version()

            # Если указан пользовательский путь к tessdata
            if self.tessdata_path and os.path.exists(self.tessdata_path):
                pytesseract.pytesseract.tesseract_cmd = self.tessdata_path
                logger.info(f"Установлен пользовательский путь к Tesseract: {self.tessdata_path}")
        except Exception as e:
            logger.error(f"Ошибка при настройке Tesseract OCR: {e}")
            logger.warning("Распознавание текста может не работать. Убедитесь, что Tesseract OCR установлен.")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения для улучшения распознавания текста.

        Args:
            image: Исходное изображение в формате numpy array

        Returns:
            Обработанное изображение
        """
        # Конвертируем в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Применяем бинаризацию для улучшения контраста текста
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Применяем морфологические операции для удаления шума
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        return processed

    def find_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Находит регионы на изображении, которые могут содержать текст.

        Args:
            image: Исходное изображение в формате numpy array

        Returns:
            Список кортежей (x, y, ширина, высота) с координатами регионов
        """
        # Предобработка изображения
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Находим контуры на изображении
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Фильтруем контуры и получаем прямоугольники, которые могут содержать текст
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Фильтруем по размеру (можно настроить в зависимости от конкретной игры)
            if w > 20 and h > 10 and w < image.shape[1] * 0.9:
                text_regions.append((x, y, w, h))

        return text_regions

    def recognize_text(self, image: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Распознает текст на изображении или в указанной области.

        Args:
            image: Исходное изображение в формате numpy array
            region: Область для распознавания в формате (x, y, ширина, высота) или None для всего изображения

        Returns:
            Распознанный текст
        """
        try:
            # Если указана область, вырезаем её
            if region:
                x, y, w, h = region
                roi = image[y:y + h, x:x + w]
            else:
                roi = image

            # Предобработка изображения
            processed = self.preprocess_image(roi)

            # Распознаем текст
            config = r'--oem 3 --psm 6'  # Режим распознавания текста построчно
            text = pytesseract.image_to_string(processed, config=config)

            # Очищаем и возвращаем результат
            return text.strip()
        except Exception as e:
            logger.error(f"Ошибка при распознавании текста: {e}")
            return ""

    def find_server_numbers(self, image: np.ndarray) -> List[Tuple[int, Tuple[int, int]]]:
        """
        Находит номера серверов на скриншоте и их координаты.

        Args:
            image: Скриншот в формате numpy array

        Returns:
            Список кортежей (номер_сервера, (x, y)) с координатами для клика
        """
        # Находим области, которые могут содержать текст
        text_regions = self.find_text_regions(image)

        server_numbers = []

        for region in text_regions:
            x, y, w, h = region

            # Распознаем текст в этой области
            text = self.recognize_text(image, region)

            # Ищем номера серверов с помощью регулярного выражения
            # Примеры: "Сервер 577", "577", "№577"
            matches = re.findall(r'(?:Сервер\s*)?(?:№\s*)?(\d{1,3})', text)

            for match in matches:
                try:
                    server_number = int(match)
                    # Координаты для клика - центр найденной области
                    click_x = x + w // 2
                    click_y = y + h // 2

                    logger.debug(f"Найден сервер {server_number} в позиции ({click_x}, {click_y})")
                    server_numbers.append((server_number, (click_x, click_y)))
                except ValueError:
                    continue

        return server_numbers

    def find_specific_server(self, image: np.ndarray, target_server: int) -> Optional[Tuple[int, int]]:
        """
        Ищет конкретный номер сервера на скриншоте.

        Args:
            image: Скриншот в формате numpy array
            target_server: Номер искомого сервера

        Returns:
            Кортеж (x, y) с координатами для клика или None, если сервер не найден
        """
        server_numbers = self.find_server_numbers(image)

        for server_number, coords in server_numbers:
            if server_number == target_server:
                logger.info(f"Найден целевой сервер {target_server} в позиции {coords}")
                return coords

        logger.debug(f"Целевой сервер {target_server} не найден на текущем экране")
        return None

    def find_season(self, image: np.ndarray, target_season: str) -> Optional[Tuple[int, int]]:
        """
        Ищет конкретный сезон на скриншоте.

        Args:
            image: Скриншот в формате numpy array
            target_season: Название искомого сезона (например, "Сезон S1")

        Returns:
            Кортеж (x, y) с координатами для клика или None, если сезон не найден
        """
        # Находим области, которые могут содержать текст
        text_regions = self.find_text_regions(image)

        for region in text_regions:
            x, y, w, h = region

            # Распознаем текст в этой области
            text = self.recognize_text(image, region)

            # Нормализуем текст для сравнения
            normalized_text = text.strip().lower()
            normalized_target = target_season.strip().lower()

            # Проверяем, содержит ли текст название сезона
            if normalized_target in normalized_text or self._fuzzy_season_match(normalized_text, normalized_target):
                # Координаты для клика - центр найденной области
                click_x = x + w // 2
                click_y = y + h // 2

                logger.info(f"Найден сезон '{target_season}' в позиции ({click_x}, {click_y})")
                return (click_x, click_y)

        logger.debug(f"Сезон '{target_season}' не найден на текущем экране")
        return None

    def _fuzzy_season_match(self, text: str, target: str) -> bool:
        """
        Нечеткое сравнение названий сезонов для улучшения распознавания.

        Args:
            text: Распознанный текст
            target: Целевой текст для поиска

        Returns:
            True, если тексты похожи, иначе False
        """
        # Разделяем на части "Сезон" и номер
        target_parts = target.split()
        if len(target_parts) != 2:
            return False

        season_word, season_number = target_parts

        # Проверяем наличие ключевого слова "сезон" или "сe3он" (OCR может ошибаться)
        if "сез" not in text and "ce3" not in text and "сeз" not in text:
            return False

        # Проверяем номер сезона (S1, X1, и т.д.)
        # OCR может путать буквы, например, "S" как "5" или "X" как "Х" (кириллица)
        if season_number.startswith("S"):
            # Ищем S1, S2, 51, 52, и т.д.
            season_num = season_number[1:]
            return re.search(r'[Ss5][' + season_num + r']', text) is not None
        elif season_number.startswith("X"):
            # Ищем X1, X2, Х1, Х2, и т.д.
            season_num = season_number[1:]
            return re.search(r'[XxХх][' + season_num + r']', text) is not None

        return False