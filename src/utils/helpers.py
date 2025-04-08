import os
import time
import random
import logging
import subprocess
import functools
from typing import List, Tuple, Optional, Dict, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


def get_connected_devices() -> List[str]:
    """
    Получает список подключенных устройств через ADB.

    Returns:
        Список идентификаторов устройств
    """
    try:
        result = subprocess.check_output("adb devices", shell=True, text=True)

        # Парсим вывод ADB
        lines = result.strip().split('\n')[1:]  # Пропускаем заголовок
        devices = []

        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2 and parts[1] == 'device':
                    devices.append(parts[0])

        return devices
    except Exception as e:
        logger.error(f"Ошибка при получении списка устройств: {e}")
        return []


def handle_exceptions(logger=None, default_return=None, show_traceback=True):
    """
    Декоратор для обработки исключений в методах.

    Args:
        logger: Логгер для записи ошибок
        default_return: Значение, возвращаемое в случае ошибки
        show_traceback: Показывать ли полный traceback

    Returns:
        Декорированная функция
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                nonlocal logger
                if logger is None:
                    # Берем логгер из logging если не передан
                    logger = logging.getLogger(__name__)

                # Логируем ошибку
                log_message = f"Ошибка в {func.__name__}: {e}"
                if show_traceback:
                    logger.error(log_message, exc_info=True)
                else:
                    logger.error(log_message)

                return default_return

        return wrapper

    return decorator


def retry(max_tries=3, delay=1, backoff=2, exceptions=(Exception,), logger=None):
    """
    Декоратор для повторного выполнения функции в случае ошибки.

    Args:
        max_tries: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Фактор увеличения задержки с каждой попыткой
        exceptions: Кортеж исключений, которые будут перехватываться
        logger: Логгер для записи ошибок

    Returns:
        Декорированная функция
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)

            tries, _delay = 0, delay
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    tries += 1
                    if tries == max_tries:
                        logger.error(f"Функция {func.__name__} не выполнена после {max_tries} попыток. Ошибка: {e}")
                        raise

                    logger.warning(
                        f"Попытка {tries}/{max_tries} для {func.__name__} не удалась. Ошибка: {e}. Повтор через {_delay} сек.")
                    time.sleep(_delay)
                    _delay *= backoff

            return None  # Этот код не должен выполняться, но для типизации

        return wrapper

    return decorator


def check_adb_installed() -> bool:
    """
    Проверяет, установлен ли ADB.

    Returns:
        True, если ADB установлен, иначе False
    """
    try:
        subprocess.check_output("adb version", shell=True, text=True)
        return True
    except:
        return False


def check_emulator_running() -> bool:
    """
    Проверяет, запущен ли эмулятор.

    Returns:
        True, если эмулятор запущен, иначе False
    """
    try:
        devices = get_connected_devices()
        return len(devices) > 0
    except:
        return False


def random_delay(min_time: float = 0.1, max_time: float = 0.5) -> None:
    """
    Выполняет случайную задержку в указанном диапазоне.

    Args:
        min_time: Минимальное время задержки (секунды)
        max_time: Максимальное время задержки (секунды)
    """
    delay = random.uniform(min_time, max_time)
    time.sleep(delay)


def format_time(seconds: float) -> str:
    """
    Форматирует время в секундах в строку вида ЧЧ:ММ:СС.

    Args:
        seconds: Время в секундах

    Returns:
        Отформатированная строка
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def get_season_for_server(server_number: int) -> str:
    """
    Определяет сезон для указанного номера сервера.

    Args:
        server_number: Номер сервера

    Returns:
        Название сезона
    """
    if server_number >= 577:
        return "Сезон S1"
    elif 541 <= server_number <= 576:
        return "Сезон S2"
    elif 505 <= server_number <= 540:
        return "Сезон S3"
    elif 481 <= server_number <= 504:
        return "Сезон S4"
    elif 433 <= server_number <= 480:
        return "Сезон S5"
    elif 409 <= server_number <= 432:
        return "Сезон X1"
    elif 266 <= server_number <= 407:
        return "Сезон X2"
    elif 1 <= server_number <= 264:
        return "Сезон X3"
    else:
        return "Неизвестный сезон"


def ensure_directory_exists(path: str) -> bool:
    """
    Проверяет существование директории и создает её при необходимости.

    Args:
        path: Путь к директории

    Returns:
        True, если директория существует или была создана, иначе False
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"Создана директория: {path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании директории {path}: {e}")
        return False


def is_game_installed(device_id: Optional[str] = None) -> bool:
    """
    Проверяет, установлена ли игра на устройстве.

    Args:
        device_id: ID устройства (если None, будет использовано первое доступное)

    Returns:
        True, если игра установлена, иначе False
    """
    try:
        # Формируем команду ADB
        cmd = f"adb{' -s ' + device_id if device_id else ''} shell pm list packages | grep com.seaofconquest.global"

        # Выполняем команду
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

        # Проверяем результат
        return "com.seaofconquest.global" in result.stdout
    except Exception as e:
        logger.error(f"Ошибка при проверке установки игры: {e}")
        return False


def format_memory_size(size_bytes: int) -> str:
    """
    Форматирует размер в байтах в человекочитаемый формат.

    Args:
        size_bytes: Размер в байтах

    Returns:
        Строка с отформатированным размером
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_timestamp() -> str:
    """
    Возвращает текущую дату и время в формате строки.

    Returns:
        Отформатированная строка с датой и временем
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_to_file(content: str, filename: str, mode: str = 'w') -> bool:
    """
    Сохраняет содержимое в файл.

    Args:
        content: Содержимое для сохранения
        filename: Имя файла
        mode: Режим открытия файла ('w' - перезапись, 'a' - добавление)

    Returns:
        True в случае успеха, False в случае ошибки
    """
    try:
        # Создаем директорию, если она не существует
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Сохраняем файл
        with open(filename, mode, encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Файл успешно сохранен: {filename}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла {filename}: {e}")
        return False