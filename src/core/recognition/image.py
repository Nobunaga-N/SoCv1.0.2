import cv2
import numpy as np
import logging
import os
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path
from src.core.recognition.base import RecognitionBase

logger = logging.getLogger(__name__)


class ImageRecognition(RecognitionBase):
    """Класс для распознавания изображений."""

    def __init__(self, assets_path: str, threshold: float = 0.8):
        """
        Инициализация класса распознавания изображений.

        Args:
            assets_path: Путь к папке с изображениями для распознавания
            threshold: Порог соответствия (0-1), где 1 - идеальное совпадение
        """
        super().__init__(threshold)
        self.assets_path = Path(assets_path)
        self.template_cache = {}  # Кэш для хранения шаблонов изображений
        self._load_templates()

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения перед распознаванием.

        Args:
            image: Исходное изображение

        Returns:
            Обработанное изображение
        """
        # В базовой реализации просто возвращаем исходное изображение
        return image.copy()

    def _load_templates(self) -> None:
        """Загружает все шаблоны изображений из папки assets в память."""
        try:
            if not self.assets_path.exists():
                os.makedirs(self.assets_path, exist_ok=True)
                logger.warning(f"Папка с активами не найдена, создана новая: {self.assets_path}")
                return

            for file_path in self.assets_path.glob("*.png"):
                try:
                    template_name = file_path.stem  # Имя файла без расширения
                    template = cv2.imread(str(file_path), cv2.IMREAD_COLOR)

                    if template is None:
                        logger.warning(f"Не удалось загрузить шаблон: {file_path}")
                        continue

                    self.template_cache[template_name] = template
                    logger.debug(f"Загружен шаблон: {template_name} ({template.shape[1]}x{template.shape[0]})")
                except Exception as e:
                    logger.error(f"Ошибка при загрузке шаблона {file_path}: {e}")

            logger.info(f"Загружено {len(self.template_cache)} шаблонов изображений")
        except Exception as e:
            logger.error(f"Ошибка при загрузке шаблонов: {e}")
            raise

    def find_template(self, screenshot: np.ndarray, template_name: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Находит шаблон на скриншоте и возвращает его координаты.

        Args:
            screenshot: Скриншот в формате numpy array
            template_name: Имя шаблона (без расширения)

        Returns:
            Кортеж (x, y, ширина, высота) или None, если шаблон не найден
        """
        if template_name not in self.template_cache:
            logger.warning(f"Шаблон не найден в кэше: {template_name}")
            return None

        template = self.template_cache[template_name]

        try:
            # Поиск шаблона на изображении
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Проверка порога соответствия
            if max_val >= self.threshold:
                w, h = template.shape[1], template.shape[0]
                x, y = max_loc
                logger.debug(f"Найден шаблон {template_name} с уверенностью {max_val:.3f} в позиции ({x}, {y})")
                return (x, y, w, h)
            else:
                logger.debug(f"Шаблон {template_name} не найден (max_val={max_val:.3f} < threshold={self.threshold})")
                return None
        except Exception as e:
            logger.error(f"Ошибка при поиске шаблона {template_name}: {e}")
            return None

    def find_all_templates(self, screenshot: np.ndarray, template_name: str, threshold: float = None) -> List[
        Tuple[int, int, int, int]]:
        """
        Находит все вхождения шаблона на скриншоте.

        Args:
            screenshot: Скриншот в формате numpy array
            template_name: Имя шаблона (без расширения)
            threshold: Порог соответствия (переопределяет стандартный)

        Returns:
            Список кортежей (x, y, ширина, высота)
        """
        if template_name not in self.template_cache:
            logger.warning(f"Шаблон не найден в кэше: {template_name}")
            return []

        template = self.template_cache[template_name]
        local_threshold = threshold if threshold is not None else self.threshold

        try:
            # Поиск шаблона на изображении
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= local_threshold)

            # Преобразуем координаты в список кортежей
            w, h = template.shape[1], template.shape[0]
            matches = []

            # Объединяем близкие совпадения
            if len(locations[0]) > 0:
                for pt in zip(*locations[::-1]):  # Меняем порядок, чтобы получить (x, y)
                    matches.append((pt[0], pt[1], w, h))

                # Группируем перекрывающиеся области с помощью нелокального подавления максимумов
                matches = self._non_max_suppression(matches)

                logger.debug(f"Найдено {len(matches)} вхождений шаблона {template_name}")
            else:
                logger.debug(f"Шаблон {template_name} не найден на изображении")

            return matches
        except Exception as e:
            logger.error(f"Ошибка при поиске всех вхождений шаблона {template_name}: {e}")
            return []

    def _non_max_suppression(self, boxes, overlap_thresh=0.3):
        """
        Применяет алгоритм нелокального подавления максимумов для объединения перекрывающихся областей.

        Args:
            boxes: Список кортежей (x, y, w, h)
            overlap_thresh: Порог перекрытия для объединения областей

        Returns:
            Отфильтрованный список областей
        """
        if len(boxes) == 0:
            return []

        # Преобразуем в формат [x1, y1, x2, y2]
        boxes_array = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

        # Получаем координаты x, y для начала и конца каждого бокса
        x1 = boxes_array[:, 0]
        y1 = boxes_array[:, 1]
        x2 = boxes_array[:, 2]
        y2 = boxes_array[:, 3]

        # Вычисляем площадь каждого бокса
        area = (x2 - x1 + 1) * (y2 - y1 + 1)

        # Сортируем индексы по области бокса (от большего к меньшему)
        idxs = np.argsort(area)[::-1]

        # Инициализируем список для хранения выбранных индексов
        pick = []

        while len(idxs) > 0:
            # Добавляем индекс в список выбранных
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            # Находим наибольшие (x, y) координаты начала и наименьшие (x, y) координаты конца
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            # Вычисляем ширину и высоту области перекрытия
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            # Вычисляем процент перекрытия
            overlap = (w * h) / area[idxs[:last]]

            # Удаляем индексы с перекрытием выше порога
            idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))

        # Преобразуем обратно в формат (x, y, w, h)
        result = [(boxes_array[i, 0], boxes_array[i, 1],
                   boxes_array[i, 2] - boxes_array[i, 0],
                   boxes_array[i, 3] - boxes_array[i, 1]) for i in pick]

        return result

    def find_and_click_template(self, emulator, screenshot: np.ndarray, template_name: str) -> bool:
        """
        Находит шаблон на скриншоте и выполняет клик по его центру.

        Args:
            emulator: Экземпляр класса Emulator для выполнения клика
            screenshot: Скриншот в формате numpy array
            template_name: Имя шаблона (без расширения)

        Returns:
            True, если шаблон найден и выполнен клик, иначе False
        """
        template_rect = self.find_template(screenshot, template_name)

        if template_rect:
            x, y, w, h = template_rect
            # Клик по центру найденного шаблона
            center_x = x + w // 2
            center_y = y + h // 2
            emulator.click(center_x, center_y)
            logger.info(f"Клик по шаблону {template_name} в позиции ({center_x}, {center_y})")
            return True
        else:
            logger.debug(f"Шаблон {template_name} не найден для клика")
            return False

    def reload_templates(self) -> None:
        """Перезагружает все шаблоны изображений из папки assets."""
        self.template_cache.clear()
        self._load_templates()