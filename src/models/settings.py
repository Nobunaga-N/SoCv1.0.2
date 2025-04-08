import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BotSettings:
    """Класс для хранения и управления настройками бота."""

    def __init__(self, config_path: str = "config.json"):
        """
        Инициализирует настройки бота.

        Args:
            config_path: Путь к файлу конфигурации
        """
        # Настройки по умолчанию
        self.ldplayer_path = None  # Путь к LDPlayer
        self.start_server = 577  # Начальный сервер (Сезон S1)
        self.end_server = 550  # Конечный сервер
        self.click_delay = 1.5  # Минимальная задержка между кликами (секунды)
        self.device_id = None  # ID устройства (None - автоматический выбор)
        self.emulator_index = "0"  # Индекс эмулятора (по умолчанию первый)
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                        "assets")
        self.tessdata_path = None  # Путь к данным Tesseract OCR (если None, используется по умолчанию)

        # Настройки интерфейса
        self.dark_theme = True  # Использовать темную тему
        self.auto_start = False  # Автоматически запускать бота при старте
        self.minimize_to_tray = False  # Сворачивать в трей при закрытии

        # Настройки логирования
        self.log_level = "INFO"  # Уровень логирования
        self.log_to_file = True  # Записывать логи в файл

        # Настройки производительности
        self.performance_monitoring = True  # Включить мониторинг производительности
        self.performance_interval = 5.0  # Интервал обновления данных о производительности (секунды)

        # Путь к файлу конфигурации
        self.config_path = config_path

        # Загружаем настройки из файла, если он существует
        self._load_settings()

    def _load_settings(self) -> None:
        """Загружает настройки из файла конфигурации."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # Обновляем настройки из файла
                for key, value in settings.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

                logger.info(f"Настройки загружены из {self.config_path}")
            else:
                logger.info("Файл конфигурации не найден, используются настройки по умолчанию")
        except Exception as e:
            logger.error(f"Ошибка при загрузке настроек: {e}")

    def save_settings(self) -> bool:
        """
        Сохраняет настройки в файл конфигурации.

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            # Создаем директорию, если ее нет
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)

            # Создаем словарь с настройками
            settings = self.to_dict()

            # Сохраняем в файл
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)

            logger.info(f"Настройки сохранены в {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует настройки в словарь.

        Returns:
            Словарь с настройками
        """
        return {
            'ldplayer_path': self.ldplayer_path,
            'start_server': self.start_server,
            'end_server': self.end_server,
            'click_delay': self.click_delay,
            'device_id': self.device_id,
            'emulator_index': self.emulator_index,
            'assets_path': self.assets_path,
            'tessdata_path': self.tessdata_path,
            'dark_theme': self.dark_theme,
            'auto_start': self.auto_start,
            'minimize_to_tray': self.minimize_to_tray,
            'log_level': self.log_level,
            'log_to_file': self.log_to_file,
            'performance_monitoring': self.performance_monitoring,
            'performance_interval': self.performance_interval
        }

    def from_dict(self, settings_dict: Dict[str, Any]) -> None:
        """
        Обновляет настройки из словаря.

        Args:
            settings_dict: Словарь с настройками
        """
        for key, value in settings_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def reset_to_defaults(self) -> None:
        """Сбрасывает настройки к значениям по умолчанию."""
        # Создаем новый объект с настройками по умолчанию
        default_settings = BotSettings("_temp_config.json")

        # Копируем атрибуты из временного объекта
        for key, value in default_settings.to_dict().items():
            if key != 'config_path':  # Сохраняем текущий путь к конфигурации
                setattr(self, key, value)

        logger.info("Настройки сброшены к значениям по умолчанию")

        # Удаляем временный файл, если он был создан
        if os.path.exists("_temp_config.json"):
            os.remove("_temp_config.json")