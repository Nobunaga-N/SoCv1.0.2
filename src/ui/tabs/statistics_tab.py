from PyQt6.QtWidgets import (QHBoxLayout, QGroupBox, QLabel, QTableWidget,
                             QTableWidgetItem, QPushButton, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

import time
from datetime import datetime

from src.ui.ui_factory import UIFactory
from src.models.statistics import BotStatistics
from src.ui.tabs.base_tab import BaseTab


class StatisticsTab(BaseTab):
    """Вкладка статистики работы бота."""

    # Сигнал для обновления статистики извне
    statistics_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Привязываем сигнал
        self.statistics_updated.connect(self.set_statistics)

        # Таймер для обновления статистики
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_statistics)
        self.update_timer.start(5000)  # Обновление каждые 5 секунд

    def _init_ui(self):
        """Инициализирует UI компоненты."""
        super()._init_ui()

        # Сводная информация
        summary_group_layout = QVBoxLayout()

        # Статус и время работы в одной строке
        status_layout = QHBoxLayout()

        # Статус бота
        status_layout.addWidget(self.ui_factory.create_label("Статус бота:"))
        self.status_label = self.ui_factory.create_label("Остановлен", True)
        self.status_label.setStyleSheet("color: #e74c3c;")  # Красный цвет для статуса "Остановлен"
        status_layout.addWidget(self.status_label)

        status_layout.addSpacing(20)

        # Время работы
        status_layout.addWidget(self.ui_factory.create_label("Время работы:"))
        self.runtime_label = self.ui_factory.create_label("00:00:00", True)
        status_layout.addWidget(self.runtime_label)

        status_layout.addStretch(1)

        summary_group_layout.addLayout(status_layout)

        # Статистика в виде таблицы
        stats_layout = QHBoxLayout()

        # Успешные сервера
        stats_layout.addWidget(self.ui_factory.create_label("Успешно:"))
        self.success_label = self.ui_factory.create_label("0", True)
        self.success_label.setStyleSheet("color: #2ecc71;")  # Зеленый цвет
        stats_layout.addWidget(self.success_label)

        stats_layout.addSpacing(20)

        # Неудачные сервера
        stats_layout.addWidget(self.ui_factory.create_label("Неудачно:"))
        self.failure_label = self.ui_factory.create_label("0", True)
        self.failure_label.setStyleSheet("color: #e74c3c;")  # Красный цвет
        stats_layout.addWidget(self.failure_label)

        stats_layout.addSpacing(20)

        # Ошибки
        stats_layout.addWidget(self.ui_factory.create_label("Ошибки:"))
        self.error_label = self.ui_factory.create_label("0", True)
        self.error_label.setStyleSheet("color: #f39c12;")  # Оранжевый цвет
        stats_layout.addWidget(self.error_label)

        stats_layout.addSpacing(20)

        # Среднее время
        stats_layout.addWidget(self.ui_factory.create_label("Среднее время:"))
        self.avg_time_label = self.ui_factory.create_label("0 сек", True)
        stats_layout.addWidget(self.avg_time_label)

        stats_layout.addStretch(1)

        summary_group_layout.addLayout(stats_layout)

        # Добавляем разделитель
        summary_group_layout.addWidget(self.ui_factory.create_horizontal_separator())

        # Диапазон серверов
        server_layout = QHBoxLayout()

        # Текущий сервер
        server_layout.addWidget(self.ui_factory.create_label("Текущий сервер:"))
        self.current_server_label = self.ui_factory.create_label("N/A", True)
        server_layout.addWidget(self.current_server_label)

        server_layout.addSpacing(20)

        # Текущий сезон
        server_layout.addWidget(self.ui_factory.create_label("Текущий сезон:"))
        self.current_season_label = self.ui_factory.create_label("N/A", True)
        server_layout.addWidget(self.current_season_label)

        server_layout.addStretch(1)

        summary_group_layout.addLayout(server_layout)

        # Группа сводной информации
        summary_group = self.ui_factory.create_group("Сводная информация", summary_group_layout)
        self.main_layout.addWidget(summary_group)

        # Таблица с завершенными серверами
        table_layout = QVBoxLayout()

        # Заголовок и кнопка очистки
        table_header_layout = QHBoxLayout()
        table_header_layout.addWidget(self.ui_factory.create_header_label("Завершенные сервера"))

        clear_button = self.ui_factory.create_button("Очистить", "Очистить таблицу")
        clear_button.clicked.connect(self._clear_table)
        table_header_layout.addWidget(clear_button)

        # Кнопка сохранения статистики
        save_button = self.ui_factory.create_button("Сохранить", "Сохранить статистику в файл")
        save_button.clicked.connect(self._save_statistics)
        table_header_layout.addWidget(save_button)

        table_layout.addLayout(table_header_layout)

        # Таблица серверов
        self.servers_table = self.ui_factory.create_table(
            ["№ сервера", "Сезон", "Статус", "Время", "Дата и время"]
        )
        table_layout.addWidget(self.servers_table)

        # Группа таблицы
        table_group = self.ui_factory.create_group("Детальная статистика", table_layout)
        self.main_layout.addWidget(table_group)

    def _update_statistics(self):
        """Обновляет отображение статистики."""
        # В реальной реализации эта функция должна быть вызвана из основного потока
        # приложения через сигналы и слоты, когда доступна новая статистика от бота
        pass

    def _clear_table(self):
        """Очищает таблицу серверов."""
        self.servers_table.setRowCount(0)
        self.logger.info("Таблица серверов очищена")

    def _save_statistics(self):
        """Сохраняет статистику в файл."""
        try:
            # Создаем временный объект статистики и заполняем его текущими данными
            stats = BotStatistics()
            stats.success_count = int(self.success_label.text())
            stats.failure_count = int(self.failure_label.text())
            stats.error_count = int(self.error_label.text())

            # Собираем историю из таблицы
            for row in range(self.servers_table.rowCount()):
                server = int(self.servers_table.item(row, 0).text())
                season = self.servers_table.item(row, 1).text()
                status = self.servers_table.item(row, 2).text()

                # Добавляем в историю
                if status == "Успешно":
                    stats.completed_servers.append(server)
                else:
                    stats.failed_servers.append(server)

                # Добавляем в полную историю
                duration = None
                duration_text = self.servers_table.item(row, 3).text()
                if duration_text.endswith(" сек"):
                    try:
                        duration = float(duration_text.replace(" сек", ""))
                    except:
                        pass

                timestamp = self.servers_table.item(row, 4).text()

                stats.server_history.append({
                    'server': server,
                    'season': season,
                    'result': 'success' if status == "Успешно" else 'failure',
                    'duration': duration,
                    'timestamp': timestamp
                })

            # Сохраняем статистику
            filename = f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if stats.save_to_file(filename):
                self.logger.info(f"Статистика успешно сохранена в файл: {filename}")
            else:
                self.logger.error("Не удалось сохранить статистику в файл")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении статистики: {e}")

    def update_bot_status(self, is_running: bool, current_server: int = None, current_season: str = None):
        """
        Обновляет статус бота.

        Args:
            is_running: True, если бот запущен, иначе False
            current_server: Текущий обрабатываемый сервер
            current_season: Текущий сезон
        """
        if is_running:
            self.status_label.setText("Запущен")
            self.status_label.setStyleSheet("color: #2ecc71;")  # Зеленый цвет для статуса "Запущен"
        else:
            self.status_label.setText("Остановлен")
            self.status_label.setStyleSheet("color: #e74c3c;")  # Красный цвет для статуса "Остановлен"

        if current_server:
            self.current_server_label.setText(str(current_server))
        else:
            self.current_server_label.setText("N/A")

        if current_season:
            self.current_season_label.setText(current_season)
        else:
            self.current_season_label.setText("N/A")

    def update_runtime(self, runtime_seconds: float):
        """
        Обновляет отображение времени работы.

        Args:
            runtime_seconds: Время работы в секундах
        """
        hours, remainder = divmod(int(runtime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        runtime_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.runtime_label.setText(runtime_str)

    def add_server_result(self, server: int, season: str, success: bool, duration: float):
        """
        Добавляет результат обработки сервера в таблицу.

        Args:
            server: Номер сервера
            season: Сезон
            success: True, если обработка успешна, иначе False
            duration: Продолжительность обработки в секундах
        """
        # Добавляем новую строку
        row = self.servers_table.rowCount()
        self.servers_table.insertRow(row)

        # Номер сервера
        self.servers_table.setItem(row, 0, QTableWidgetItem(str(server)))

        # Сезон
        self.servers_table.setItem(row, 1, QTableWidgetItem(season))

        # Статус
        status_item = QTableWidgetItem("Успешно" if success else "Неудачно")
        status_item.setForeground(Qt.GlobalColor.darkGreen if success else Qt.GlobalColor.darkRed)
        self.servers_table.setItem(row, 2, status_item)

        # Время
        self.servers_table.setItem(row, 3, QTableWidgetItem(f"{duration:.1f} сек"))

        # Дата и время
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.servers_table.setItem(row, 4, QTableWidgetItem(current_time))

        # Прокручиваем таблицу к новой строке
        self.servers_table.scrollToItem(self.servers_table.item(row, 0))

    def set_statistics(self, stats: dict):
        """
        Устанавливает данные статистики.

        Args:
            stats: Словарь с данными статистики
        """
        if not stats:
            return

        # Обновляем сводную информацию
        self.success_label.setText(str(stats.get('success_count', 0)))
        self.failure_label.setText(str(stats.get('failure_count', 0)))
        self.error_label.setText(str(stats.get('error_count', 0)))

        # Среднее время
        avg_time = stats.get('avg_time')
        if avg_time is not None:
            self.avg_time_label.setText(f"{avg_time:.1f} сек")
        else:
            self.avg_time_label.setText("0 сек")

        # Текущий прогресс
        if 'current_server' in stats and stats['current_server'] is not None:
            self.current_server_label.setText(str(stats['current_server']))
        else:
            self.current_server_label.setText("N/A")

        if 'current_season' in stats and stats['current_season'] is not None:
            self.current_season_label.setText(stats['current_season'])
        else:
            self.current_season_label.setText("N/A")

        # Обновляем таблицу
        server_history = stats.get('server_history', [])

        # Очищаем таблицу, если история пуста
        if not server_history:
            self.servers_table.setRowCount(0)
            return

        # Добавляем новые записи в таблицу
        for entry in server_history:
            # Проверяем, есть ли уже эта запись в таблице
            server_number = entry.get('server')
            timestamp = entry.get('timestamp')

            # Ищем эту запись в таблице
            found = False
            for row in range(self.servers_table.rowCount()):
                if (self.servers_table.item(row, 0).text() == str(server_number) and
                        self.servers_table.item(row, 4).text() == timestamp):
                    found = True
                    break

            # Если записи нет, добавляем
            if not found:
                success = entry.get('result') == 'success'
                duration = entry.get('duration', 0)
                season = entry.get('season', "")

                self.add_server_result(server_number, season, success, duration)