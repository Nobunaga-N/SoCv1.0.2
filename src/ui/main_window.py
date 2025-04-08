import sys
import os
import logging
import threading
import time
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QPushButton, QLabel,
                             QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QTextCursor

from src.ui.ui_factory import UIFactory
from src.ui.styles import Styles
from src.ui.tabs.statistics_tab import StatisticsTab
from src.ui.tabs.control_tab import ControlTab
from src.ui.tabs.advanced_tab import AdvancedTab
from src.core.bot import SeaConquestBot
from src.models.settings import BotSettings
from src.utils.logger import setup_logger


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self, bot=None):
        super().__init__()

        self.ui_factory = UIFactory()

        # Настройки бота
        self.settings = BotSettings()

        # Бот
        self.bot = bot

        # Флаг запуска бота
        self.is_bot_running = False

        # Время запуска бота
        self.bot_start_time = None

        # Настройка логирования
        self.logger = logging.getLogger(__name__)

        # Инициализация UI
        self._init_ui()

        # Таймер для обновления времени работы
        self.runtime_timer = QTimer(self)
        self.runtime_timer.timeout.connect(self._update_runtime)

    def _init_ui(self):
        """Инициализирует UI компоненты."""
        self.setWindowTitle("Sea of Conquest Bot")
        self.setGeometry(100, 100, 1000, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной макет
        main_layout = QVBoxLayout(central_widget)

        # Вкладки
        self.tab_widget = QTabWidget()

        # Вкладка управления
        self.control_tab = ControlTab()
        self.tab_widget.addTab(self.control_tab, "Управление")

        # Вкладка статистики
        self.statistics_tab = StatisticsTab()
        self.tab_widget.addTab(self.statistics_tab, "Статистика")

        # Вкладка расширенного управления (включает в себя настройки)
        self.advanced_tab = AdvancedTab(self.settings)
        self.tab_widget.addTab(self.advanced_tab, "Настройки и управление")

        main_layout.addWidget(self.tab_widget)

        # Привязываем сигналы вкладок
        self._connect_signals()

        # Применяем темную тему
        Styles.apply_dark_theme(QApplication.instance())

    def _connect_signals(self):
        """Привязывает сигналы вкладок к слотам главного окна."""
        # Сигналы вкладки управления
        self.control_tab.start_bot_signal.connect(self._start_bot)
        self.control_tab.stop_bot_signal.connect(self._stop_bot)
        self.control_tab.pause_bot_signal.connect(self._toggle_pause)

        # Сигналы вкладки расширенного управления
        self.advanced_tab.restart_emulator_signal.connect(self._on_restart_emulator)
        self.advanced_tab.check_resources_signal.connect(self._on_check_resources)
        self.advanced_tab.settings_changed.connect(self._on_settings_changed)

    def start_bot(self):
        """Публичный метод для запуска бота (может вызываться извне)."""
        if not self.is_bot_running:
            self._start_bot()

    def _start_bot(self):
        """Запускает бота."""
        if self.is_bot_running:
            self.logger.warning("Бот уже запущен")
            return

        try:
            # Создаем бота, если его еще нет
            if self.bot is None:
                from src.core.bot_factory import BotFactory
                self.bot = BotFactory.create_bot(self.settings)

                if not self.bot:
                    self.logger.error("Не удалось создать бота")
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать бота")
                    return

            # Запускаем бота
            self.bot.start()

            # Обновляем UI
            self.is_bot_running = True
            self.bot_start_time = datetime.now()

            # Обновляем состояние кнопок в control_tab
            self.control_tab.set_bot_running_state(True)

            # Запускаем таймер обновления времени работы
            self.runtime_timer.start(1000)  # Каждую секунду

            # Обновляем статус в статистике
            self.statistics_tab.update_bot_status(
                True, self.bot.current_server, self.bot.current_season
            )

            # Обновляем информацию о текущем сервере и сезоне
            self.control_tab.update_server_info(self.bot.current_server, self.bot.current_season)

            self.logger.info(f"Бот запущен. Начинаем с сервера {self.bot.current_server} ({self.bot.current_season})")

        except Exception as e:
            self.logger.error(f"Ошибка при запуске бота: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить бота: {e}")

    def _stop_bot(self):
        """Останавливает бота."""
        if not self.is_bot_running or not self.bot:
            self.logger.warning("Бот не запущен")
            return

        try:
            # Останавливаем бота
            self.bot.stop()

            # Обновляем UI
            self.is_bot_running = False
            self.runtime_timer.stop()

            # Обновляем состояние кнопок в control_tab
            self.control_tab.set_bot_running_state(False)

            # Обновляем статус в статистике
            self.statistics_tab.update_bot_status(False)

            # Получаем статистику
            if self.bot:
                stats = self.bot.get_statistics()
                self.statistics_tab.set_statistics(stats)

            self.logger.info("Бот остановлен")

        except Exception as e:
            self.logger.error(f"Ошибка при остановке бота: {e}")

    def _toggle_pause(self):
        """Переключает состояние паузы бота."""
        if not self.is_bot_running or not self.bot:
            return

        try:
            if self.bot.paused:
                # Возобновляем работу
                self.bot.resume()
                self.control_tab.set_bot_running_state(True, False)
                self.logger.info("Бот возобновлен")
            else:
                # Приостанавливаем работу
                self.bot.pause()
                self.control_tab.set_bot_running_state(True, True)
                self.logger.info("Бот приостановлен")
        except Exception as e:
            self.logger.error(f"Ошибка при переключении паузы: {e}")

    def _update_runtime(self):
        """Обновляет отображение времени работы бота."""
        if self.bot_start_time:
            runtime = datetime.now() - self.bot_start_time
            runtime_seconds = runtime.total_seconds()

            # Обновляем метку времени в статистике
            self.statistics_tab.update_runtime(runtime_seconds)

            # Обновляем информацию о текущем сервере и сезоне, если бот запущен
            if self.is_bot_running and self.bot:
                self.control_tab.update_server_info(
                    self.bot.current_server,
                    self.bot.current_season
                )

                # Обновляем статус в статистике
                self.statistics_tab.update_bot_status(
                    True,
                    self.bot.current_server,
                    self.bot.current_season
                )

                # Получаем текущую статистику и обновляем вкладку статистики
                stats = self.bot.get_statistics()
                if stats:
                    self.statistics_tab.set_statistics(stats)

    def _on_settings_changed(self, new_settings):
        """Обрабатывает изменение настроек."""
        self.settings = new_settings
        self.logger.info("Настройки обновлены")

        # Если бот уже создан, обновляем его настройки
        if self.bot:
            self.bot.settings = new_settings
            # Добавляем эти строки для обновления текущего сервера и сезона
            self.bot.current_server = new_settings.start_server
            self.bot.current_season = self.bot._get_season_for_server(self.bot.current_server)

            # Обновляем информацию на UI
            self.control_tab.update_server_info(self.bot.current_server, self.bot.current_season)

            self.logger.info(
                f"Настройки бота обновлены, текущий сервер: {self.bot.current_server}, "
                f"сезон: {self.bot.current_season}"
            )

    def _on_restart_emulator(self):
        """Обрабатывает сигнал о перезапуске эмулятора."""
        # Если бот запущен, останавливаем его
        if self.is_bot_running:
            self._stop_bot()

        self.logger.info("Эмулятор перезапущен, требуется повторная инициализация бота")

        # Через 5 секунд пробуем заново создать бота
        QTimer.singleShot(5000, self._reinitialize_bot)

    def _reinitialize_bot(self):
        """Переинициализирует бота после перезапуска эмулятора."""
        try:
            # Создаем бота заново
            from src.core.bot_factory import BotFactory
            self.bot = BotFactory.create_bot(self.settings)

            if self.bot:
                self.logger.info("Бот переинициализирован успешно")
            else:
                self.logger.error("Не удалось переинициализировать бота")
        except Exception as e:
            self.logger.error(f"Ошибка при переинициализации бота: {e}")

    def _on_check_resources(self):
        """Обрабатывает сигнал о проверке ресурсов."""
        # Здесь можно добавить логику для оптимизации работы бота
        # в зависимости от доступных ресурсов
        self.logger.info("Проверка ресурсов выполнена")

    def closeEvent(self, event):
        """Обрабатывает событие закрытия окна."""
        if self.is_bot_running and self.bot:
            reply = QMessageBox.question(
                self, 'Подтверждение выхода',
                "Бот все еще работает. Остановить и выйти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Останавливаем бота перед выходом
                self._stop_bot()

                # Останавливаем мониторинг производительности
                if hasattr(self.advanced_tab, 'performance_monitor'):
                    self.advanced_tab.performance_monitor.stop()

                event.accept()
            else:
                event.ignore()
        else:
            # Останавливаем мониторинг производительности
            if hasattr(self.advanced_tab, 'performance_monitor'):
                self.advanced_tab.performance_monitor.stop()

            event.accept()