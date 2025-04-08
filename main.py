#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import argparse
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.ui.main_window import MainWindow
from src.models.settings import BotSettings
from src.utils.logger import setup_logger
from src.utils.helpers import ensure_directory_exists


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Sea of Conquest Bot')
    parser.add_argument('--config', type=str, help='Путь к файлу конфигурации')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='Уровень логирования')
    parser.add_argument('--no-gui', action='store_true', help='Запуск без графического интерфейса')
    parser.add_argument('--auto-start', action='store_true', help='Автоматический запуск бота при старте')
    return parser.parse_args()


def setup_environment():
    """Настройка окружения для работы приложения."""
    # Создаем необходимые директории
    ensure_directory_exists('logs')
    ensure_directory_exists('assets')
    ensure_directory_exists('config')


def main():
    """Основная функция запуска приложения."""
    # Парсим аргументы командной строки
    args = parse_arguments()

    # Настраиваем окружение
    setup_environment()

    # Настраиваем логирование
    log_level = getattr(logging, args.log_level)
    logger = setup_logger(log_level, True)
    logger.info(f"Sea of Conquest Bot запущен с уровнем логирования {args.log_level}")

    # Загружаем настройки
    config_path = args.config if args.config else "config/config.json"
    settings = BotSettings(config_path)

    # Обновляем настройки из аргументов командной строки
    if args.auto_start:
        settings.auto_start = True

    # Запускаем приложение
    if not args.no_gui:
        # Запуск GUI версии
        app = QApplication(sys.argv)
        app.setApplicationName("Sea of Conquest Bot")

        # Устанавливаем иконку приложения, если она есть
        icon_path = os.path.join(settings.assets_path, "icon.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        # Создаем главное окно
        main_window = MainWindow()
        main_window.show()

        # Если нужно автоматически запустить бота
        if settings.auto_start:
            logger.info("Автоматический запуск бота...")
            main_window.start_bot()

        # Запускаем главный цикл приложения
        return app.exec()
    else:
        # Запуск консольной версии (пока не реализовано)
        logger.error("Консольный режим пока не реализован")
        return 1

if __name__ == "__main__":
    sys.exit(main())