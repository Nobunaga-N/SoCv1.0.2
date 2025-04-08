import sys
import os
import logging
import subprocess
from typing import Dict, Tuple, List, Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QPushButton, QTabWidget, QComboBox,
                             QSpinBox, QFileDialog, QMessageBox, QTextEdit,
                             QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from src.ui.tabs.base_tab import BaseTab
from src.utils.ldplayer import LDPlayer
from src.utils.performance import PerformanceMonitor
from src.models.settings import BotSettings
from src.ui.ui_factory import UIFactory

class LDPlayerDiagnosticsDialog(QDialog):
    """Диалоговое окно для диагностики LDPlayer"""

    def __init__(self, ldplayer_path: str, parent=None):
        super().__init__(parent)
        self.ldplayer_path = ldplayer_path
        self.setWindowTitle("Диагностика LDPlayer")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Текстовое поле для вывода результатов диагностики
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Кнопки для запуска диагностических тестов
        buttons_layout = QHBoxLayout()

        self.check_path_button = QPushButton("Проверить путь")
        self.check_path_button.clicked.connect(self.check_path)
        buttons_layout.addWidget(self.check_path_button)

        self.run_list_button = QPushButton("Запустить 'list'")
        self.run_list_button.clicked.connect(self.run_list_command)
        buttons_layout.addWidget(self.run_list_button)

        self.run_direct_button = QPushButton("Прямой запуск ldconsole")
        self.run_direct_button.clicked.connect(self.run_direct_command)
        buttons_layout.addWidget(self.run_direct_button)

        layout.addLayout(buttons_layout)

        # Стандартные кнопки диалога
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        # Запускаем первичную проверку
        self.check_path()

    def append_output(self, text: str):
        """Добавляет текст в окно вывода"""
        self.output_text.append(text)

    def check_path(self):
        """Проверяет правильность указанного пути"""
        self.output_text.clear()
        self.append_output(f"=== Проверка пути к LDPlayer ===\n")

        # Проверка существования пути
        self.append_output(f"Указанный путь: {self.ldplayer_path}")
        if not os.path.exists(self.ldplayer_path):
            self.append_output("ОШИБКА: Путь не существует!")
            return

        self.append_output("✓ Путь существует")

        # Проверка существования ldconsole.exe
        ldconsole_path = os.path.join(self.ldplayer_path, "ldconsole.exe")
        self.append_output(f"Путь к ldconsole.exe: {ldconsole_path}")

        if not os.path.exists(ldconsole_path):
            self.append_output("ОШИБКА: Файл ldconsole.exe не найден!")
            return

        self.append_output("✓ Файл ldconsole.exe найден")

        # Проверка возможности выполнения
        self.append_output(f"\nПроверка доступа к ldconsole.exe...")
        try:
            if os.access(ldconsole_path, os.X_OK):
                self.append_output("✓ Права на выполнение есть")
            else:
                self.append_output("⚠ Предупреждение: возможно отсутствуют права на выполнение")
        except Exception as e:
            self.append_output(f"Ошибка при проверке прав доступа: {str(e)}")

    def run_list_command(self):
        """Запускает команду list через LDPlayerHelper"""
        self.output_text.clear()
        self.append_output("=== Запуск команды list через LDPlayer ===\n")

        try:
            ldplayer = LDPlayer(self.ldplayer_path)

            if not ldplayer.is_available():
                self.append_output("ОШИБКА: LDPlayer недоступен")
                return

            self.append_output("LDPlayer доступен, запуск команды list...\n")

            # Выполняем команду
            success, result = ldplayer._run_ldconsole_command("list")

            if success:
                self.append_output(f"Команда выполнена успешно!\nРезультат:\n{result}")

                # Анализируем результат
                if not result.strip():
                    self.append_output("\n⚠ ВНИМАНИЕ: Пустой результат. Возможно, нет настроенных эмуляторов.")
                    self.append_output("Откройте LDPlayer Manager и создайте хотя бы один эмулятор.")
            else:
                self.append_output(f"ОШИБКА при выполнении команды:\n{result}")

        except Exception as e:
            self.append_output(f"Исключение при выполнении команды: {str(e)}")

    def run_direct_command(self):
        """Напрямую запускает ldconsole.exe через subprocess"""
        self.output_text.clear()
        self.append_output("=== Прямой запуск ldconsole.exe ===\n")

        ldconsole_path = os.path.join(self.ldplayer_path, "ldconsole.exe")

        if not os.path.exists(ldconsole_path):
            self.append_output("ОШИБКА: Файл ldconsole.exe не найден!")
            return

        self.append_output(f"Запуск команды: \"{ldconsole_path}\" list\n")

        try:
            # Запускаем процесс с перехватом stdout и stderr
            process = subprocess.Popen(
                f'"{ldconsole_path}" list',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(timeout=10)

            self.append_output(f"Код возврата: {process.returncode}\n")

            if stdout:
                self.append_output(f"Стандартный вывод:\n{stdout}")
            else:
                self.append_output("Стандартный вывод пуст")

            if stderr:
                self.append_output(f"Стандартная ошибка:\n{stderr}")

            if process.returncode != 0:
                self.append_output("\n⚠ ВНИМАНИЕ: Команда завершилась с ошибкой!")

            if not stdout.strip() and process.returncode == 0:
                self.append_output(
                    "\n⚠ ВНИМАНИЕ: Пустой вывод команды. Проверьте, есть ли настроенные эмуляторы в LDPlayer.")

        except subprocess.TimeoutExpired:
            self.append_output("ОШИБКА: Превышено время ожидания (10 секунд)")
        except Exception as e:
            self.append_output(f"Исключение при выполнении команды: {str(e)}")


class AdvancedTab(QWidget):
    """Вкладка расширенного управления и настроек."""

    # Сигналы
    restart_emulator_signal = pyqtSignal()
    check_resources_signal = pyqtSignal()
    settings_changed = pyqtSignal(object)

    # Словарь сезонов и соответствующих им диапазонов серверов
    SEASONS = {
        "Сезон S1": (577, 600),
        "Сезон S2": (541, 576),
        "Сезон S3": (505, 540),
        "Сезон S4": (481, 504),
        "Сезон S5": (433, 480),
        "Сезон X1": (409, 432),
        "Сезон X2": (266, 407),
        "Сезон X3": (1, 264),
    }

    # Типичные пути установки LDPlayer
    COMMON_LDPLAYER_PATHS = [
        "C:\\LDPlayer\\LDPlayer9",
        "C:\\LDPlayer9",
        "C:\\Program Files\\LDPlayer\\LDPlayer9",
        "C:\\Program Files (x86)\\LDPlayer\\LDPlayer9",
        os.path.expanduser("~\\LDPlayer\\LDPlayer9"),
        "D:\\LDPlayer\\LDPlayer9",
    ]

    def __init__(self, settings: BotSettings, parent=None):
        """
        Инициализирует вкладку расширенного управления.

        Args:
            settings: Настройки бота
            parent: Родительский виджет
        """
        super().__init__(parent)

        self.settings = settings
        self.ui_factory = UIFactory()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Создаем основной макет
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Инициализируем helper после проверки/установки пути
        self.ldplayer_path = self.settings.ldplayer_path or self._find_ldplayer_path_manually()
        self.ldplayer = LDPlayer(self.ldplayer_path)

        # Инициализируем монитор производительности
        self.performance_monitor = PerformanceMonitor(
            interval=settings.performance_interval,
            enable_logging=settings.performance_monitoring
        )

        if settings.performance_monitoring:
            self.performance_monitor.start()

        # Таймер для обновления данных об эмуляторах
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._refresh_emulators)
        self.update_timer.start(10000)  # Обновление каждые 10 секунд

        # Инициализируем UI
        self._init_ui()

    def _create_group(self, title, layout, add_to_main=True):
        """
        Создает группу с заданным заголовком и макетом.

        Args:
            title: Заголовок группы
            layout: Макет для группы
            add_to_main: Добавлять ли группу сразу в основной макет

        Returns:
            Созданная группа
        """
        group = self.ui_factory.create_group(title, layout)

        if add_to_main and hasattr(self, 'main_layout'):
            self.main_layout.addWidget(group)

        return group

    def _create_horizontal_layout(self, add_to_main=False):
        """
        Создает горизонтальный макет.

        Args:
            add_to_main: Добавлять ли макет сразу в основной макет

        Returns:
            Созданный макет
        """
        layout = QHBoxLayout()

        if add_to_main and hasattr(self, 'main_layout'):
            self.main_layout.addLayout(layout)

        return layout

    def _create_vertical_layout(self, add_to_main=False):
        """
        Создает вертикальный макет.

        Args:
            add_to_main: Добавлять ли макет сразу в основной макет

        Returns:
            Созданный макет
        """
        layout = QVBoxLayout()

        if add_to_main and hasattr(self, 'main_layout'):
            self.main_layout.addLayout(layout)

        return layout

    def _find_ldplayer_path_manually(self) -> Optional[str]:
        """
        Ищет путь к LDPlayer вручную, проверяя наиболее распространенные места установки.

        Returns:
            Путь к LDPlayer или None, если не найден
        """
        # Пробуем найти в стандартных местах
        for path in self.COMMON_LDPLAYER_PATHS:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "ldconsole.exe")):
                logging.info(f"Найден LDPlayer по пути: {path}")
                return path

        # Пробуем найти через команду where (если LDPlayer в PATH)
        try:
            result = subprocess.check_output("where ldconsole.exe", shell=True, text=True, stderr=subprocess.PIPE)
            if result:
                path = os.path.dirname(result.strip().split('\n')[0])
                logging.info(f"Найден LDPlayer через PATH: {path}")
                return path
        except subprocess.CalledProcessError:
            pass

        logging.warning("Не удалось автоматически найти LDPlayer")
        return None

    def _init_ui(self):
        """Инициализирует компоненты интерфейса."""
        # Создаем вкладки для различных функций
        tabs = QTabWidget()

        # Вкладка управления эмулятором (с интегрированными настройками)
        emulator_tab = self._create_emulator_tab()
        tabs.addTab(emulator_tab, "Эмулятор")

        # Вкладка мониторинга ресурсов
        performance_tab = self._create_performance_tab()
        tabs.addTab(performance_tab, "Мониторинг ресурсов")

        self.main_layout.addWidget(tabs)

    def _create_emulator_tab(self) -> QWidget:
        """
        Создает упрощенную вкладку управления эмулятором с настройками серверов.

        Returns:
            Виджет вкладки
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Группа выбора эмулятора
        emulator_group_layout = QVBoxLayout()

        # Выбор эмулятора
        select_layout = QHBoxLayout()
        select_layout.addWidget(self.ui_factory.create_label("Эмулятор:"))
        self.emulator_combo = self.ui_factory.create_combobox(["Поиск эмуляторов..."])
        select_layout.addWidget(self.emulator_combo, 1)  # Растягиваем по горизонтали

        # Кнопка обновления списка эмуляторов
        refresh_button = self.ui_factory.create_button("Обновить", "Обновить список эмуляторов")
        refresh_button.clicked.connect(self._refresh_emulators)
        select_layout.addWidget(refresh_button)

        emulator_group_layout.addLayout(select_layout)

        # Путь к LDPlayer
        ldpath_layout = QHBoxLayout()
        ldpath_layout.addWidget(self.ui_factory.create_label("Путь к LDPlayer:"))
        self.ldplayer_path_label = self.ui_factory.create_label(
            self.ldplayer_path or "Не найден")
        ldpath_layout.addWidget(self.ldplayer_path_label, 1)  # Растягиваем по горизонтали

        # Кнопка выбора пути к LDPlayer
        browse_ldpath_button = self.ui_factory.create_button("Обзор", "Выбрать путь к LDPlayer")
        browse_ldpath_button.clicked.connect(self._browse_ldplayer_path)
        ldpath_layout.addWidget(browse_ldpath_button)

        emulator_group_layout.addLayout(ldpath_layout)

        # Статус LDPlayer и кнопка диагностики
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.ui_factory.create_label("Статус LDPlayer:"))
        self.ldplayer_status_label = self.ui_factory.create_label(
            "Активен" if self.ldplayer.is_available() else "Недоступен", True)

        # Устанавливаем цвет в зависимости от статуса
        if self.ldplayer.is_available():
            self.ldplayer_status_label.setStyleSheet("color: #2ecc71;")  # Зеленый
        else:
            self.ldplayer_status_label.setStyleSheet("color: #e74c3c;")  # Красный

        status_layout.addWidget(self.ldplayer_status_label)

        # Кнопка диагностики
        diagnose_button = self.ui_factory.create_button("Диагностика", "Запустить диагностику LDPlayer")
        diagnose_button.clicked.connect(self._run_diagnostics)
        status_layout.addWidget(diagnose_button)

        status_layout.addStretch(1)

        emulator_group_layout.addLayout(status_layout)

        # Добавляем информационный блок, если LDPlayer не найден
        if not self.ldplayer.is_available():
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            info_text.setMaximumHeight(80)
            info_text.setFont(QFont("Segoe UI", 9))
            info_text.setText(
                "LDPlayer не найден или недоступен. Пожалуйста, выберите путь к папке LDPlayer вручную, "
                "используя кнопку 'Обзор'. Обычно LDPlayer устанавливается в 'C:\\LDPlayer\\LDPlayer9' "
                "или 'C:\\Program Files\\LDPlayer\\LDPlayer9'. В выбранной папке должен находиться файл ldconsole.exe."
            )
            emulator_group_layout.addWidget(info_text)

        # Группа настроек сезона и серверов
        server_group_layout = QVBoxLayout()

        # Выбор сезона
        season_layout = QHBoxLayout()
        season_layout.addWidget(self.ui_factory.create_label("Сезон:"))
        self.season_combo = self.ui_factory.create_combobox(list(self.SEASONS.keys()))
        season_layout.addWidget(self.season_combo, 1)  # Растягиваем по горизонтали

        # Кнопка установки сезона
        set_season_button = self.ui_factory.create_button("Установить", "Установить выбранный сезон")
        set_season_button.clicked.connect(self._set_season)
        season_layout.addWidget(set_season_button)

        server_group_layout.addLayout(season_layout)

        # Диапазон серверов
        server_range_layout = QHBoxLayout()
        server_range_layout.addWidget(self.ui_factory.create_label("Начальный сервер:"))
        self.start_server_spinbox = self.ui_factory.create_spinbox(1, 600, self.settings.start_server)
        server_range_layout.addWidget(self.start_server_spinbox)

        server_range_layout.addWidget(self.ui_factory.create_label("Конечный сервер:"))
        self.end_server_spinbox = self.ui_factory.create_spinbox(1, 600, self.settings.end_server)
        server_range_layout.addWidget(self.end_server_spinbox)

        server_group_layout.addLayout(server_range_layout)

        server_info_label = self.ui_factory.create_label(
            "Примечание: В игре серверы нумеруются по убыванию. Начинайте с большего номера и заканчивайте меньшим.",
            False, 9
        )
        server_info_label.setStyleSheet("color: #7f8c8d;")  # Серый цвет
        server_group_layout.addWidget(server_info_label)

        # Задержка между кликами
        click_delay_layout = QHBoxLayout()
        click_delay_layout.addWidget(self.ui_factory.create_label("Задержка между кликами (сек):"))
        self.click_delay_spinbox = self.ui_factory.create_spinbox(
            1, 10, int(self.settings.click_delay), step=1,
            tooltip="Минимальная задержка между кликами"
        )
        click_delay_layout.addWidget(self.click_delay_spinbox)
        click_delay_layout.addStretch(1)

        server_group_layout.addLayout(click_delay_layout)

        # Кнопки сохранения/сброса настроек
        settings_buttons_layout = QHBoxLayout()
        settings_buttons_layout.addStretch(1)

        reset_button = self.ui_factory.create_button("Сбросить", "Сбросить настройки по умолчанию")
        reset_button.clicked.connect(self._reset_settings)
        settings_buttons_layout.addWidget(reset_button)

        save_button = self.ui_factory.create_button("Сохранить", "Сохранить настройки")
        save_button.clicked.connect(self._save_settings)
        settings_buttons_layout.addWidget(save_button)

        # Создаем группы и добавляем в основной макет
        emulator_group = self.ui_factory.create_group("LDPlayer и выбор эмулятора", emulator_group_layout)
        server_settings_group = self.ui_factory.create_group("Настройки серверов", server_group_layout)

        layout.addWidget(emulator_group)
        layout.addWidget(server_settings_group)
        layout.addLayout(settings_buttons_layout)
        layout.addStretch(1)

        # Сразу обновляем список эмуляторов
        self._refresh_emulators()

        # Подключаем сигнал изменения сезона
        self.season_combo.currentIndexChanged.connect(self._update_server_range)

        # Инициализируем диапазон серверов на основе выбранного сезона
        self._update_server_range()

        return tab

    def _create_performance_tab(self) -> QWidget:
        """
        Создает вкладку мониторинга ресурсов системы.

        Returns:
            Виджет вкладки
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Группа информации о системе
        system_group = QGroupBox("Информация о системе")
        system_layout = QVBoxLayout()

        # Загрузка CPU
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("Загрузка CPU:"))
        self.cpu_label = QLabel("0%")
        self.cpu_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(QLabel("Процесс бота:"))
        self.process_cpu_label = QLabel("0%")
        self.process_cpu_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cpu_layout.addWidget(self.process_cpu_label)
        cpu_layout.addStretch(1)
        system_layout.addLayout(cpu_layout)

        # Использование памяти
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Использование памяти:"))
        self.memory_label = QLabel("0%")
        self.memory_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        memory_layout.addWidget(self.memory_label)
        memory_layout.addWidget(QLabel("Процесс бота:"))
        self.process_memory_label = QLabel("0%")
        self.process_memory_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        memory_layout.addWidget(self.process_memory_label)
        memory_layout.addStretch(1)
        system_layout.addLayout(memory_layout)

        # Использование диска
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Использование диска:"))
        self.disk_label = QLabel("0%")
        self.disk_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        disk_layout.addWidget(self.disk_label)
        disk_layout.addStretch(1)
        system_layout.addLayout(disk_layout)

        # Информация о системе
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Ядра CPU:"))
        self.cpu_cores_label = QLabel("N/A")
        info_layout.addWidget(self.cpu_cores_label)
        info_layout.addSpacing(20)
        info_layout.addWidget(QLabel("Память:"))
        self.memory_total_label = QLabel("N/A")
        info_layout.addWidget(self.memory_total_label)
        info_layout.addStretch(1)
        system_layout.addLayout(info_layout)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # Группа управления мониторингом
        monitoring_group = QGroupBox("Управление мониторингом")
        monitoring_layout = QVBoxLayout()

        # Настройки мониторинга
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Интервал обновления (сек):"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(60)
        self.interval_spinbox.setValue(int(self.settings.performance_interval))
        settings_layout.addWidget(self.interval_spinbox)
        settings_layout.addStretch(1)
        monitoring_layout.addLayout(settings_layout)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.start_monitoring_button = QPushButton("Запустить мониторинг")
        self.start_monitoring_button.clicked.connect(self._toggle_monitoring)
        buttons_layout.addWidget(self.start_monitoring_button)

        self.check_resources_button = QPushButton("Проверить ресурсы")
        self.check_resources_button.clicked.connect(self._check_resources)
        buttons_layout.addWidget(self.check_resources_button)

        buttons_layout.addStretch(1)
        monitoring_layout.addLayout(buttons_layout)

        monitoring_group.setLayout(monitoring_layout)
        layout.addWidget(monitoring_group)

        # Таймер для обновления метрик производительности
        self.performance_timer = QTimer(self)
        self.performance_timer.timeout.connect(self._update_performance_metrics)
        self.performance_timer.start(1000)  # Обновление каждую секунду

        # Получаем информацию о системе
        if self.performance_monitor:
            system_info = self.performance_monitor.get_system_info()
            if system_info:
                # Заполняем информацию о системе
                cores = system_info.get('cpu', {})
                memory = system_info.get('memory', {})

                if cores:
                    cpu_info = f"{cores.get('cores_physical', 'N/A')} физич, {cores.get('cores_logical', 'N/A')} логич"
                    self.cpu_cores_label.setText(cpu_info)

                if memory:
                    total_memory = self.performance_monitor.format_memory_size(memory.get('total', 0))
                    self.memory_total_label.setText(total_memory)

        # Обновляем состояние кнопки мониторинга
        self._update_monitoring_button_state()

        layout.addStretch(1)
        return tab

    def _run_diagnostics(self):
        """Запускает диалоговое окно диагностики LDPlayer"""
        dialog = LDPlayerDiagnosticsDialog(
            self.ldplayer_path or "",
            parent=self
        )
        dialog.exec()

    def _check_emulator_running(self, index: str) -> bool:
        """Проверяет, запущен ли эмулятор с указанным индексом."""
        if not self.ldplayer.is_available():
            return False

        return self.ldplayer.is_running(index)

    def _refresh_emulators(self):
        """Обновляет список эмуляторов напрямую через subprocess."""
        try:
            # Проверяем, доступен ли путь к LDPlayer
            if not self.ldplayer.is_available():
                self.emulator_combo.clear()
                self.emulator_combo.addItem("LDPlayer не найден")
                self.ldplayer_status_label.setText("Недоступен")
                self.ldplayer_status_label.setStyleSheet("color: #e74c3c;")  # Красный
                return

            # Сохраняем текущий выбранный элемент
            current_index = self.emulator_combo.currentIndex()
            current_text = self.emulator_combo.currentText() if current_index >= 0 else None

            # Очищаем комбобокс
            self.emulator_combo.clear()

            # Получаем список эмуляторов через LDPlayer
            emulators = self.ldplayer.list_emulators()

            # Обновляем статус LDPlayer
            self.ldplayer_status_label.setText("Активен")
            self.ldplayer_status_label.setStyleSheet("color: #2ecc71;")  # Зеленый

            # Обрабатываем список эмуляторов
            if emulators:
                for emulator in emulators:
                    status = emulator.get('status', 'stopped')
                    name = emulator.get('name', 'Неизвестный')
                    index = emulator.get('index', '0')
                    self.emulator_combo.addItem(f"{name} ({status})", userData=index)

                # Восстанавливаем выбранный элемент, если возможно
                if current_text and self.emulator_combo.count() > 0:
                    for i in range(self.emulator_combo.count()):
                        if current_text in self.emulator_combo.itemText(i):
                            self.emulator_combo.setCurrentIndex(i)
                            break

                self.logger.info(f"Найдено {len(emulators)} эмуляторов")
            else:
                self.emulator_combo.addItem("Нет доступных эмуляторов")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении списка эмуляторов: {e}")
            self.emulator_combo.clear()
            self.emulator_combo.addItem(f"Ошибка: {str(e)}")

    def _browse_ldplayer_path(self):
        """Открывает диалог выбора пути к LDPlayer."""
        initial_dir = self.ldplayer_path_label.text()
        if initial_dir == "Не найден":
            initial_dir = "C:\\"

        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку LDPlayer", initial_dir
        )

        if folder:
            # Проверяем, есть ли ldconsole.exe в выбранной папке
            if not os.path.exists(os.path.join(folder, "ldconsole.exe")):
                QMessageBox.warning(
                    self,
                    "Некорректный путь",
                    "В выбранной папке не найден файл ldconsole.exe.\n"
                    "Пожалуйста, выберите корректную папку установки LDPlayer."
                )
                return

            self.ldplayer_path_label.setText(folder)
            self.ldplayer_path = folder
            self.logger.info(f"Выбрана новая папка LDPlayer: {folder}")

            # Переинициализируем LDPlayer с новым путем
            self.ldplayer = LDPlayer(folder)

            # Обновляем статус
            if self.ldplayer.is_available():
                self.ldplayer_status_label.setText("Активен")
                self.ldplayer_status_label.setStyleSheet("color: #2ecc71;")  # Зеленый
            else:
                self.ldplayer_status_label.setText("Недоступен")
                self.ldplayer_status_label.setStyleSheet("color: #e74c3c;")  # Красный

            # Обновляем список эмуляторов
            self._refresh_emulators()

    def _force_refresh_emulators(self):
        """Принудительно обновляет список эмуляторов с прямым запросом через subprocess."""
        self.logger.info("Принудительное обновление списка эмуляторов...")

        if not self.ldplayer_path or not os.path.exists(self.ldplayer_path):
            self.logger.error(f"Путь к LDPlayer не найден: {self.ldplayer_path}")
            return

        ldconsole_path = os.path.join(self.ldplayer_path, "ldconsole.exe")
        if not os.path.exists(ldconsole_path):
            self.logger.error(f"ldconsole.exe не найден по пути: {ldconsole_path}")
            return

        try:
            # Очищаем и обновляем статус
            self.emulator_combo.clear()

            # Запускаем команду list напрямую
            cmd = f'"{ldconsole_path}" list'
            self.logger.info(f"Выполнение команды: {cmd}")

            result = subprocess.check_output(cmd, shell=True, text=True, encoding='utf-8')
            self.logger.info(f"Результат команды list: {result}")

            # Анализируем результат
            lines = result.strip().split('\n')
            for line in lines:
                if line.strip():
                    self.logger.info(f"Добавление эмулятора: {line}")
                    parts = line.split(',') if ',' in line else line.split()
                    index = parts[0] if parts else "0"
                    name = parts[1] if len(parts) > 1 else f"Эмулятор {index}"
                    self.emulator_combo.addItem(f"{name} (неизвестно)", userData=index)

            # Если ничего не добавили, добавляем эмулятор по умолчанию
            if self.emulator_combo.count() == 0:
                self.emulator_combo.addItem("LDPlayer (по умолчанию)", userData="0")

            self.logger.info(f"Найдено {self.emulator_combo.count()} эмуляторов")

        except Exception as e:
            self.logger.error(f"Ошибка при принудительном обновлении списка эмуляторов: {e}")
            self.emulator_combo.addItem(f"Ошибка: {str(e)}")

    def _update_server_range(self):
        """Обновляет диапазон серверов в зависимости от выбранного сезона."""
        current_season = self.season_combo.currentText()

        if current_season in self.SEASONS:
            min_server, max_server = self.SEASONS[current_season]

            # Обновляем диапазоны спинбоксов
            self.start_server_spinbox.setMinimum(min_server)
            self.start_server_spinbox.setMaximum(max_server)
            self.end_server_spinbox.setMinimum(min_server)
            self.end_server_spinbox.setMaximum(max_server)

            # Всегда устанавливаем начальный сервер на максимум и конечный на минимум
            # при выборе нового сезона
            self.start_server_spinbox.setValue(max_server)
            self.end_server_spinbox.setValue(min_server)

            # Добавляем информационную подсказку к спинбоксам
            self.start_server_spinbox.setToolTip(f"Начинать с сервера (диапазон {min_server}-{max_server})")
            self.end_server_spinbox.setToolTip(f"Заканчивать сервером (диапазон {min_server}-{max_server})")

            self.logger.debug(f"Обновлен диапазон серверов для сезона {current_season}: {min_server}-{max_server}")

    def _set_season(self):
        """Устанавливает выбранный сезон и обновляет диапазон серверов."""
        self._update_server_range()
        self.logger.info(f"Установлен сезон {self.season_combo.currentText()}")

    def _save_settings(self):
        """Сохраняет настройки и отправляет сигнал об изменении."""
        try:
            # Обновляем объект настроек
            self.settings.start_server = self.start_server_spinbox.value()
            self.settings.end_server = self.end_server_spinbox.value()
            self.settings.click_delay = float(self.click_delay_spinbox.value())
            self.settings.ldplayer_path = self.ldplayer_path

            # Настройки мониторинга
            self.settings.performance_interval = float(self.interval_spinbox.value())

            # Получаем индекс выбранного эмулятора и сохраняем его
            index = self.emulator_combo.currentIndex()
            if index >= 0:
                emulator_index = self.emulator_combo.itemData(index)
                if emulator_index:
                    self.settings.emulator_index = emulator_index

            # Сохраняем настройки в файл
            self.settings.save_settings()

            # Отправляем сигнал об изменении настроек
            self.settings_changed.emit(self.settings)

            self.logger.info("Настройки успешно сохранены")
            QMessageBox.information(self, "Настройки", "Настройки успешно сохранены")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")

    def _reset_settings(self):
        """Сбрасывает настройки по умолчанию."""
        try:
            # Сбрасываем настройки к значениям по умолчанию
            self.settings.reset_to_defaults()

            # Обновляем UI
            self.start_server_spinbox.setValue(self.settings.start_server)
            self.end_server_spinbox.setValue(self.settings.end_server)
            self.click_delay_spinbox.setValue(int(self.settings.click_delay))
            self.interval_spinbox.setValue(int(self.settings.performance_interval))

            # Сбрасываем выбор сезона к первому варианту
            self.season_combo.setCurrentIndex(0)
            self._update_server_range()

            self.logger.info("Настройки сброшены к значениям по умолчанию")
            QMessageBox.information(self, "Настройки", "Настройки сброшены к значениям по умолчанию")
        except Exception as e:
            self.logger.error(f"Ошибка при сбросе настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сбросить настройки: {e}")

    def _update_performance_metrics(self):
        """Обновляет метрики производительности на UI."""
        if not self.performance_monitor:
            return

        # Получаем текущие метрики
        metrics = self.performance_monitor.get_metrics()

        # Обновляем UI
        self.cpu_label.setText(f"{metrics.get('cpu_usage', 0):.1f}%")
        self.memory_label.setText(f"{metrics.get('memory_usage', 0):.1f}%")
        self.disk_label.setText(f"{metrics.get('disk_usage', 0):.1f}%")
        self.process_cpu_label.setText(f"{metrics.get('process_cpu_usage', 0):.1f}%")
        self.process_memory_label.setText(f"{metrics.get('process_memory_usage', 0):.1f}%")

        # Устанавливаем цвета в зависимости от значений
        # CPU
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 90:
            self.cpu_label.setStyleSheet("color: #e74c3c;")  # Красный
        elif cpu_usage > 70:
            self.cpu_label.setStyleSheet("color: #f39c12;")  # Оранжевый
        else:
            self.cpu_label.setStyleSheet("color: #2ecc71;")  # Зеленый

        # Память
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 90:
            self.memory_label.setStyleSheet("color: #e74c3c;")  # Красный
        elif memory_usage > 70:
            self.memory_label.setStyleSheet("color: #f39c12;")  # Оранжевый
        else:
            self.memory_label.setStyleSheet("color: #2ecc71;")  # Зеленый

    def _toggle_monitoring(self):
        """Включает/выключает мониторинг ресурсов."""
        if self.performance_monitor.running:
            self.performance_monitor.stop()
            self.logger.info("Мониторинг производительности остановлен")
        else:
            # Обновляем интервал из UI
            self.performance_monitor.interval = float(self.interval_spinbox.value())
            self.performance_monitor.start()
            self.logger.info("Мониторинг производительности запущен")

        # Обновляем состояние кнопки
        self._update_monitoring_button_state()

    def _check_resources(self):
        """Проверяет наличие достаточных ресурсов для работы бота."""
        if not self.performance_monitor:
            QMessageBox.warning(self, "Ошибка", "Мониторинг ресурсов недоступен")
            return

        # Обновляем метрики
        self.performance_monitor.update_metrics()

        # Проверяем ресурсы
        if self.performance_monitor.check_resources():
            QMessageBox.information(
                self,
                "Проверка ресурсов",
                "Системные ресурсы в норме и достаточны для работы бота."
            )
        else:
            QMessageBox.warning(
                self,
                "Проверка ресурсов",
                "Обнаружена нехватка системных ресурсов!\n\n"
                f"CPU: {self.performance_monitor.cpu_usage:.1f}%\n"
                f"Память: {self.performance_monitor.memory_usage:.1f}%\n"
                f"Диск: {self.performance_monitor.disk_usage:.1f}%\n\n"
                "Это может негативно повлиять на стабильность работы бота."
            )

        # Отправляем сигнал для возможной обработки в основном окне
        self.check_resources_signal.emit()

    def _update_monitoring_button_state(self):
        """Обновляет состояние кнопки мониторинга."""
        if self.performance_monitor and self.performance_monitor.running:
            self.start_monitoring_button.setText("Остановить мониторинг")
            self.start_monitoring_button.setStyleSheet("background-color: #e74c3c; color: white;")
        else:
            self.start_monitoring_button.setText("Запустить мониторинг")
            self.start_monitoring_button.setStyleSheet("")