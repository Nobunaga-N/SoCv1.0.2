import logging
import time
import subprocess
from typing import Tuple, List, Optional, Dict, Any
import os
import re

from src.utils.adb import ADB
from src.utils.ldplayer import LDPlayer

logger = logging.getLogger(__name__)


class Emulator:
    """Класс для управления эмулятором через ADB и LDPlayer."""

    def __init__(self, device_id: Optional[str] = None, ldplayer_path: Optional[str] = None):
        """
        Инициализация объекта для управления эмулятором.

        Args:
            device_id: Идентификатор устройства для ADB (если None, будет получен автоматически)
            ldplayer_path: Путь к директории LDPlayer (если None, будет найден автоматически)
        """
        # Инициализация LDPlayer
        self.ldplayer = LDPlayer(ldplayer_path)
        self.ldplayer_index = "0"  # По умолчанию используем первый эмулятор

        # Получаем device_id, если не указан
        if device_id is None and self.ldplayer.is_available():
            device_id = self.ldplayer.get_device_id(self.ldplayer_index)
            if device_id:
                logger.info(f"Автоматически получен device_id: {device_id}")
            else:
                logger.warning("Не удалось автоматически получить device_id")

        # Инициализация ADB
        self.adb = ADB(device_id)

        # Настройки
        self.min_action_interval = 1.5  # Минимальный интервал между действиями (секунды)
        self.last_action_time = 0

        logger.info(f"Эмулятор инициализирован. LDPlayer: {self.ldplayer.is_available()}, ADB: {device_id}")

    def get_device_id(self) -> Optional[str]:
        """
        Возвращает текущий device_id.

        Returns:
            Идентификатор устройства или None
        """
        return self.adb.device_id

    def check_connection(self) -> bool:
        """
        Проверяет подключение к эмулятору.

        Returns:
            True, если подключение активно, иначе False
        """
        if not self.adb.device_id:
            # Пробуем получить device_id через LDPlayer
            if self.ldplayer.is_available():
                device_id = self.ldplayer.get_device_id(self.ldplayer_index)
                if device_id:
                    self.adb.device_id = device_id
                    logger.info(f"Обновлен device_id: {device_id}")
                    return True
                else:
                    logger.error("Не удалось получить device_id")
                    return False
            return False

        # Проверяем подключение через ADB
        success, _ = self.adb.execute_adb_command("devices")
        return success and self.adb.device_id in _

    def wait_for_interval(self) -> None:
        """Ожидает минимальный интервал между действиями."""
        current_time = time.time()
        time_since_last_action = current_time - self.last_action_time

        # Если не прошло достаточно времени с последнего действия, ждем
        if time_since_last_action < self.min_action_interval:
            sleep_time = self.min_action_interval - time_since_last_action
            logger.debug(f"Ожидание {sleep_time:.2f} сек. перед следующим действием")
            time.sleep(sleep_time)

    def get_screenshot(self) -> bytes:
        """
        Делает скриншот экрана эмулятора.

        Returns:
            Скриншот в виде байтов
        """
        self.wait_for_interval()
        try:
            screenshot = self.adb.get_screenshot()
            self.last_action_time = time.time()
            return screenshot
        except Exception as e:
            logger.error(f"Ошибка при получении скриншота: {e}")
            raise

    def click(self, x: int, y: int) -> bool:
        """
        Выполняет клик по указанным координатам.

        Args:
            x: Координата X
            y: Координата Y

        Returns:
            True в случае успеха, False в случае ошибки
        """
        self.wait_for_interval()
        success = self.adb.click(x, y)
        self.last_action_time = time.time()
        return success

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 500) -> bool:
        """
        Выполняет свайп от одних координат к другим.

        Args:
            start_x: Начальная координата X
            start_y: Начальная координата Y
            end_x: Конечная координата X
            end_y: Конечная координата Y
            duration_ms: Продолжительность свайпа в миллисекундах

        Returns:
            True в случае успеха, False в случае ошибки
        """
        self.wait_for_interval()
        success = self.adb.swipe(start_x, start_y, end_x, end_y, duration_ms)
        self.last_action_time = time.time()
        return success

    def complex_swipe(self, points: List[Tuple[int, int]], duration_ms: int = 1000) -> bool:
        """
        Выполняет сложный свайп через несколько точек.

        Args:
            points: Список кортежей (x, y) для промежуточных точек свайпа
            duration_ms: Общая продолжительность свайпа в миллисекундах

        Returns:
            True в случае успеха, False в случае ошибки
        """
        if len(points) < 2:
            logger.error("Для свайпа требуется минимум 2 точки")
            return False

        self.wait_for_interval()

        try:
            # Разбиваем общий свайп на серию свайпов между соседними точками
            segment_duration = duration_ms // (len(points) - 1)
            success = True

            for i in range(len(points) - 1):
                start_x, start_y = points[i]
                end_x, end_y = points[i + 1]
                result = self.adb.swipe(start_x, start_y, end_x, end_y, segment_duration)
                success = success and result
                time.sleep(0.1)  # Небольшая пауза между сегментами

            logger.info(f"Сложный свайп через {len(points)} точек")
            self.last_action_time = time.time()
            return success
        except Exception as e:
            logger.error(f"Ошибка при выполнении сложного свайпа: {e}")
            return False

    def press_esc(self) -> bool:
        """
        Отправляет нажатие клавиши ESC (эквивалент BACK в Android).

        Returns:
            True в случае успеха, False в случае ошибки
        """
        return self.adb.press_esc()

    def press_key(self, key_code: int) -> bool:
        """
        Отправляет нажатие клавиши на устройство.

        Args:
            key_code: Код клавиши Android

        Returns:
            True в случае успеха, False в случае ошибки
        """
        return self.adb.press_key(key_code)

    def start_app(self, package_name: str, activity_name: Optional[str] = None) -> bool:
        """
        Запускает приложение на устройстве.

        Args:
            package_name: Имя пакета приложения
            activity_name: Имя активности (если нужно запустить конкретную)

        Returns:
            True в случае успеха, False в случае ошибки
        """
        return self.adb.start_app(package_name, activity_name)

    def close_app(self, package_name: str) -> bool:
        """
        Закрывает приложение на устройстве.

        Args:
            package_name: Имя пакета приложения

        Returns:
            True в случае успеха, False в случае ошибки
        """
        return self.adb.close_app(package_name)

    def is_app_installed(self, package_name: str) -> bool:
        """
        Проверяет, установлено ли приложение на устройстве.

        Args:
            package_name: Имя пакета приложения

        Returns:
            True, если приложение установлено, иначе False
        """
        return self.ldplayer.is_app_installed(package_name, self.ldplayer_index)

    def restart_emulator(self) -> bool:
        """
        Перезапускает эмулятор.

        Returns:
            True в случае успеха, False в случае ошибки
        """
        if not self.ldplayer.is_available():
            logger.error("LDPlayer недоступен")
            return False

        logger.info("Перезапуск эмулятора")
        success = self.ldplayer.reboot(self.ldplayer_index)

        if success:
            # Обновляем device_id после перезапуска
            new_device_id = self.ldplayer.get_device_id(self.ldplayer_index)
            if new_device_id:
                self.adb.device_id = new_device_id
                logger.info(f"Обновлен device_id после перезапуска: {new_device_id}")
            else:
                logger.warning("Не удалось получить device_id после перезапуска")

        return success