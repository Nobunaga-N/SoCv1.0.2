import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QTextEdit


class QTextEditLogger(logging.Handler, QObject):
    """
    Обработчик логов для отображения в QTextEdit.
    """

    append_signal = pyqtSignal(str)

    def __init__(self, text_edit: QTextEdit):
        """
        Инициализирует обработчик.

        Args:
            text_edit: Виджет QTextEdit для отображения логов
        """
        logging.Handler.__init__(self)
        QObject.__init__(self)

        self.text_edit = text_edit
        self.append_signal.connect(self.text_edit.append)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Отправляет запись лога в QTextEdit.

        Args:
            record: Запись лога
        """
        msg = self.format(record)

        # Добавляем цвет в зависимости от уровня лога
        if record.levelno >= logging.ERROR:
            msg = f'<span style="color: #e74c3c;">{msg}</span>'
        elif record.levelno >= logging.WARNING:
            msg = f'<span style="color: #f39c12;">{msg}</span>'
        elif record.levelno >= logging.INFO:
            msg = f'<span style="color: #2ecc71;">{msg}</span>'

        self.append_signal.emit(msg)


def setup_logger(log_level: int = logging.INFO, log_to_file: bool = True) -> logging.Logger:
    """
    Настраивает систему логирования.

    Args:
        log_level: Уровень логирования
        log_to_file: Флаг записи логов в файл

    Returns:
        Настроенный логгер
    """
    # Создаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Очищаем существующие обработчики
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Создаем форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

    # Добавляем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Если включена запись в файл
    if log_to_file:
        try:
            # Создаем папку для логов, если её нет
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # Имя файла логов с датой
            log_file = log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"

            # Создаем обработчик для записи в файл с ротацией
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 МБ
                backupCount=5
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Не удалось настроить запись логов в файл: {e}")

    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    Адаптер для добавления дополнительного контекста в логи.
    """

    def __init__(self, logger: logging.Logger, context: dict = None):
        """
        Инициализирует адаптер.

        Args:
            logger: Базовый логгер
            context: Словарь с контекстной информацией
        """
        super().__init__(logger, context or {})

    def process(self, msg, kwargs):
        """
        Обрабатывает сообщение, добавляя контекст.

        Args:
            msg: Сообщение
            kwargs: Дополнительные аргументы

        Returns:
            Кортеж (обработанное сообщение, обработанные аргументы)
        """
        # Добавляем контекстную информацию к сообщению
        if self.extra:
            context_str = ' '.join([f"[{k}={v}]" for k, v in self.extra.items()])
            msg = f"{msg} {context_str}"

        return msg, kwargs


def get_bot_logger(bot_id: str, server: int = None) -> logging.LoggerAdapter:
    """
    Создает адаптер логгера для конкретного бота.

    Args:
        bot_id: Идентификатор бота
        server: Номер текущего сервера

    Returns:
        Адаптер логгера с контекстом
    """
    logger = logging.getLogger(f"bot.{bot_id}")

    # Создаем контекст
    context = {'bot_id': bot_id}
    if server is not None:
        context['server'] = server

    return LoggerAdapter(logger, context)


def add_text_edit_handler(text_edit: QTextEdit, level: int = logging.INFO) -> QTextEditLogger:
    """
    Добавляет обработчик логов для отображения в QTextEdit.

    Args:
        text_edit: Виджет QTextEdit для отображения логов
        level: Уровень логирования

    Returns:
        Созданный обработчик
    """
    log_handler = QTextEditLogger(text_edit)
    log_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    log_handler.setFormatter(formatter)

    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)

    return log_handler