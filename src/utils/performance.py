import os
import time
import psutil
import logging
import threading
import platform
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Класс для мониторинга производительности и ресурсов системы."""

    def __init__(self, interval: float = 5.0, enable_logging: bool = False,
                 history_length: int = 60):
        """
        Инициализация монитора производительности.

        Args:
            interval: Интервал обновления данных (секунды)
            enable_logging: Включить логирование данных о производительности
            history_length: Количество точек истории для хранения
        """
        self.interval = interval
        self.enable_logging = enable_logging
        self.running = False
        self._stop_event = threading.Event()
        self._thread = None

        # Данные о производительности
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = 0.0
        self.process_cpu_usage = 0.0
        self.process_memory_usage = 0.0

        # История использования ресурсов
        self.history_length = history_length
        self.cpu_history = []  # type: List[Tuple[float, float]]
        self.memory_history = []  # type: List[Tuple[float, float]]

        # Получаем текущий процесс
        self.process = psutil.Process(os.getpid())

    def start(self) -> None:
        """Запускает мониторинг производительности в отдельном потоке."""
        if self.running:
            logger.warning("Монитор производительности уже запущен")
            return

        self.running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("Монитор производительности запущен")

    def stop(self) -> None:
        """Останавливает мониторинг производительности."""
        if not self.running:
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)  # Ждем завершения потока не более 2 секунд

        self.running = False
        logger.info("Монитор производительности остановлен")

    def _monitor_loop(self) -> None:
        """Основной цикл сбора данных о производительности."""
        while not self._stop_event.is_set() and self.running:
            try:
                self.update_metrics()
                if self.enable_logging:
                    self.log_metrics()

                # Обновляем историю
                current_time = time.time()
                self.cpu_history.append((current_time, self.cpu_usage))
                self.memory_history.append((current_time, self.memory_usage))

                # Ограничиваем размер истории
                if len(self.cpu_history) > self.history_length:
                    self.cpu_history.pop(0)
                if len(self.memory_history) > self.history_length:
                    self.memory_history.pop(0)

                # Ждем до следующего обновления
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(self.interval)

    def update_metrics(self) -> None:
        """Обновляет метрики производительности."""
        try:
            # Общая загрузка CPU (в процентах)
            self.cpu_usage = psutil.cpu_percent()

            # Общее использование памяти (в процентах)
            memory = psutil.virtual_memory()
            self.memory_usage = memory.percent

            # Использование диска (в процентах)
            disk = psutil.disk_usage('/')
            self.disk_usage = disk.percent

            # Использование ресурсов текущим процессом
            self.process_cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
            self.process_memory_usage = self.process.memory_percent()
        except Exception as e:
            logger.error(f"Ошибка при обновлении метрик: {e}")

    def log_metrics(self) -> None:
        """Логирует метрики производительности."""
        logger.debug(
            f"CPU: {self.cpu_usage:.1f}%, Память: {self.memory_usage:.1f}%, "
            f"Диск: {self.disk_usage:.1f}%, Процесс CPU: {self.process_cpu_usage:.1f}%, "
            f"Процесс Память: {self.process_memory_usage:.1f}%"
        )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Возвращает текущие метрики производительности.

        Returns:
            Словарь с метриками
        """
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'process_cpu_usage': self.process_cpu_usage,
            'process_memory_usage': self.process_memory_usage,
            'cpu_history': self.cpu_history.copy(),
            'memory_history': self.memory_history.copy()
        }

    def get_system_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о системе.

        Returns:
            Словарь с информацией о системе
        """
        try:
            # Получаем информацию о системе
            cpu_info = {
                'cores_physical': psutil.cpu_count(logical=False),
                'cores_logical': psutil.cpu_count(logical=True),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None
            }

            memory_info = {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available
            }

            disk_info = {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free
            }

            return {
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'platform': {
                    'system': psutil.WINDOWS if os.name == 'nt' else psutil.LINUX if os.name == 'posix' else 'Unknown',
                    'python_version': platform.python_version()
                }
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о системе: {e}")
            return {}

    def check_resources(self) -> bool:
        """
        Проверяет, достаточно ли ресурсов для работы бота.

        Returns:
            True, если ресурсов достаточно, иначе False
        """
        try:
            # Обновляем метрики
            self.update_metrics()

            # Проверяем критические значения
            if self.cpu_usage > 95:  # CPU загружен более чем на 95%
                logger.warning(f"Критическая загрузка CPU: {self.cpu_usage:.1f}%")
                return False

            if self.memory_usage > 90:  # Память заполнена более чем на 90%
                logger.warning(f"Критическое использование памяти: {self.memory_usage:.1f}%")
                return False

            if self.disk_usage > 95:  # Диск заполнен более чем на 95%
                logger.warning(f"Критическое использование диска: {self.disk_usage:.1f}%")
                return False

            # Проверяем доступную память (должно быть не менее 500MB)
            available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
            if available_memory_mb < 500:
                logger.warning(f"Недостаточно свободной памяти: {available_memory_mb:.1f} MB")
                return False

            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке ресурсов: {e}")
            return True  # В случае ошибки считаем, что ресурсов достаточно

    def format_memory_size(self, size_bytes: int) -> str:
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