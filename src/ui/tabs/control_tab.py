from typing import Optional
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTextEdit, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QTextCursor

from src.ui.tabs.base_tab import BaseTab
from src.ui.styles import Styles
from src.utils.logger import add_text_edit_handler


class ControlTab(BaseTab):
    """Вкладка управления ботом."""

    # Сигналы
    start_bot_signal = pyqtSignal()
    stop_bot_signal = pyqtSignal()
    pause_bot_signal = pyqtSignal()

    # Сигнал для обновления лога из другого потока
    log_message_signal = pyqtSignal(str)

    # Сигнал для обновления информации о текущем шаге
    step_update_signal = pyqtSignal(int, str)

    # Сигнал для обновления прогресса шага
    step_progress_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Привязываем сигналы
        self.log_message_signal.connect(self._append_log)
        self.step_update_signal.connect(self._update_step_info)
        self.step_progress_signal.connect(self._update_step_progress)

    def _init_ui(self):
        """Инициализирует UI компоненты."""
        super()._init_ui()

        # Верхняя панель с информацией о боте
        info_layout = QHBoxLayout()

        # Информация о версии
        info_layout.addWidget(self.ui_factory.create_label("Sea of Conquest Bot v2.0"))

        info_layout.addStretch(1)

        # Информация о текущем сервере
        info_layout.addWidget(self.ui_factory.create_label("Текущий сервер:"))
        self.current_server_label = self.ui_factory.create_label("Не выбран", True)
        info_layout.addWidget(self.current_server_label)

        info_layout.addSpacing(10)

        # Информация о текущем сезоне
        info_layout.addWidget(self.ui_factory.create_label("Сезон:"))
        self.current_season_label = self.ui_factory.create_label("Не выбран", True)
        info_layout.addWidget(self.current_season_label)

        self.main_layout.addLayout(info_layout)

        # Разделительная линия
        self.main_layout.addWidget(self.ui_factory.create_horizontal_separator())

        # Верхняя панель с кнопками
        buttons_layout = QHBoxLayout()

        # Кнопка старта
        self.start_button = self.ui_factory.create_button("Запустить бота", "Запустить бота")
        self.start_button.setStyleSheet(Styles.get_stylesheets()['start_button'])
        self.start_button.clicked.connect(self._on_start_clicked)
        buttons_layout.addWidget(self.start_button)

        # Кнопка паузы
        self.pause_button = self.ui_factory.create_button("Пауза", "Приостановить бота", enabled=False)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        buttons_layout.addWidget(self.pause_button)

        # Кнопка остановки
        self.stop_button = self.ui_factory.create_button("Остановить", "Остановить бота", enabled=False)
        self.stop_button.setStyleSheet(Styles.get_stylesheets()['stop_button'])
        self.stop_button.clicked.connect(self._on_stop_clicked)
        buttons_layout.addWidget(self.stop_button)

        buttons_layout.addStretch(1)

        self.main_layout.addLayout(buttons_layout)

        # Группа текущего шага
        step_layout = QHBoxLayout()
        step_layout.addWidget(self.ui_factory.create_label("Текущий шаг:"))
        self.current_step_label = self.ui_factory.create_label("Нет активных шагов", True)
        step_layout.addWidget(self.current_step_label)

        # Прогресс выполнения шага
        step_layout.addWidget(self.ui_factory.create_label("Прогресс:"))
        self.step_progress = self.ui_factory.create_progressbar(0, 100, 0)
        self.step_progress.setMaximumWidth(200)
        step_layout.addWidget(self.step_progress)

        self.main_layout.addLayout(step_layout)

        # Журнал работы
        log_group_layout = QVBoxLayout()

        # Текстовое поле для журнала
        self.log_textedit = self.ui_factory.create_textedit(True, "Лог работы бота...")
        self.log_textedit.setStyleSheet(Styles.get_stylesheets()['text_edit'])
        log_group_layout.addWidget(self.log_textedit)

        # Кнопки для работы с журналом
        log_buttons_layout = QHBoxLayout()

        # Кнопка очистки журнала
        clear_log_button = self.ui_factory.create_button("Очистить лог", "Очистить журнал работы")
        clear_log_button.clicked.connect(self._clear_log)
        log_buttons_layout.addWidget(clear_log_button)

        # Кнопка сохранения журнала
        save_log_button = self.ui_factory.create_button("Сохранить лог", "Сохранить журнал в файл")
        save_log_button.clicked.connect(self._save_log)
        log_buttons_layout.addWidget(save_log_button)

        log_buttons_layout.addStretch(1)

        log_group_layout.addLayout(log_buttons_layout)

        # Группа журнала
        log_group = self.ui_factory.create_group("Журнал работы", log_group_layout)
        self.main_layout.addWidget(log_group)

        # Настройка обработчика логов для текстового поля
        self.log_handler = add_text_edit_handler(self.log_textedit)

        # Добавляем сообщение о запуске
        self.logger.info("Приложение запущено. Для начала работы нажмите 'Запустить бота'.")

    def _on_start_clicked(self):
        """Обработчик нажатия кнопки 'Запустить'."""
        # Проверка на готовность системы к запуску бота
        self.start_bot_signal.emit()

    def _on_pause_clicked(self):
        """Обработчик нажатия кнопки 'Пауза'/'Продолжить'."""
        self.pause_bot_signal.emit()

    def _on_stop_clicked(self):
        """Обработчик нажатия кнопки 'Остановить'."""
        # Запрашиваем подтверждение
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите остановить бота?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.stop_bot_signal.emit()

    def _clear_log(self):
        """Очищает журнал работы."""
        self.log_textedit.clear()
        self.logger.info("Журнал очищен")

    def _save_log(self):
        """Сохраняет журнал работы в файл."""
        try:
            import os
            from datetime import datetime

            # Создаем папку logs, если ее нет
            os.makedirs("logs", exist_ok=True)

            # Формируем имя файла с текущей датой и временем
            filename = f"logs/bot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            # Сохраняем содержимое журнала в файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_textedit.toPlainText())

            self.logger.info(f"Журнал сохранен в файл: {filename}")
            QMessageBox.information(self, "Сохранение", f"Журнал успешно сохранен в файл:\n{filename}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении журнала: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить журнал: {e}")

    @pyqtSlot(str)
    def _append_log(self, text):
        """Добавляет текст в журнал работы."""
        self.log_textedit.append(text)
        # Прокручиваем к последней строке
        self.log_textedit.moveCursor(QTextCursor.MoveOperation.End)

    @pyqtSlot(int, str)
    def _update_step_info(self, step_id, description):
        """Обновляет информацию о текущем шаге."""
        self.current_step_label.setText(f"Шаг {step_id}: {description}")

    @pyqtSlot(int)
    def _update_step_progress(self, percent):
        """Обновляет прогресс выполнения текущего шага."""
        self.step_progress.setValue(percent)

    def set_bot_running_state(self, running: bool, paused: bool = False):
        """
        Обновляет состояние кнопок и индикаторов в зависимости от состояния бота.

        Args:
            running: True, если бот запущен
            paused: True, если бот на паузе
        """
        if running:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.pause_button.setEnabled(True)

            if paused:
                self.pause_button.setText("Продолжить")
            else:
                self.pause_button.setText("Пауза")
        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.pause_button.setText("Пауза")

    def update_server_info(self, server: Optional[int] = None, season: Optional[str] = None):
        """
        Обновляет информацию о текущем сервере и сезоне.

        Args:
            server: Номер текущего сервера
            season: Название текущего сезона
        """
        if server is not None:
            self.current_server_label.setText(str(server))
        else:
            self.current_server_label.setText("Не выбран")

        if season is not None:
            self.current_season_label.setText(season)
        else:
            self.current_season_label.setText("Не выбран")