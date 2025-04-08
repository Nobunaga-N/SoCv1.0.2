import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import os


class BotStatistics:
    """Класс для хранения статистики работы бота."""

    def __init__(self):
        """Инициализирует объект статистики."""
        self.success_count = 0  # Количество успешно пройденных обучений
        self.failure_count = 0  # Количество неудачных попыток
        self.error_count = 0  # Количество ошибок

        self.completed_servers = []  # Список успешно пройденных серверов
        self.failed_servers = []  # Список неудачных серверов
        self.server_history = []  # История обработки серверов с временем и результатом

        self.total_time = 0.0  # Общее время работы (секунды)
        self.start_time = time.time()  # Время начала работы
        self.last_update = time.time()  # Время последнего обновления

        # Текущий прогресс
        self.current_server = None  # Текущий обрабатываемый сервер
        self.current_season = None  # Текущий сезон
        self.current_step = None  # Текущий шаг обучения

    def update_timestamp(self) -> None:
        """Обновляет временную метку последнего обновления."""
        self.last_update = time.time()

    def reset(self) -> None:
        """Сбрасывает всю статистику."""
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0

        self.completed_servers.clear()
        self.failed_servers.clear()
        self.server_history.clear()

        self.total_time = 0.0
        self.start_time = time.time()
        self.last_update = time.time()

        self.current_server = None
        self.current_season = None
        self.current_step = None

    def add_success(self, server: int, duration: float) -> None:
        """
        Добавляет успешное прохождение обучения.

        Args:
            server: Номер сервера
            duration: Продолжительность (секунды)
        """
        self.success_count += 1
        self.completed_servers.append(server)
        self.total_time += duration

        # Добавляем в историю
        self.server_history.append({
            'server': server,
            'season': self._get_season_for_server(server),
            'result': 'success',
            'duration': duration,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        self.update_timestamp()

    def add_failure(self, server: int, reason: str = "") -> None:
        """
        Добавляет неудачное прохождение обучения.

        Args:
            server: Номер сервера
            reason: Причина неудачи
        """
        self.failure_count += 1
        self.failed_servers.append(server)

        # Добавляем в историю
        self.server_history.append({
            'server': server,
            'season': self._get_season_for_server(server),
            'result': 'failure',
            'reason': reason,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        self.update_timestamp()

    def add_error(self, error_message: str = "") -> None:
        """
        Увеличивает счетчик ошибок.

        Args:
            error_message: Сообщение об ошибке
        """
        self.error_count += 1

        # Добавляем информацию об ошибке в историю, если известен текущий сервер
        if self.current_server:
            self.server_history.append({
                'server': self.current_server,
                'season': self.current_season,
                'result': 'error',
                'error_message': error_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        self.update_timestamp()

    def set_current_progress(self, server: Optional[int] = None, season: Optional[str] = None,
                             step: Optional[int] = None) -> None:
        """
        Устанавливает текущий прогресс бота.

        Args:
            server: Текущий сервер
            season: Текущий сезон
            step: Текущий шаг обучения
        """
        if server is not None:
            self.current_server = server
        if season is not None:
            self.current_season = season
        if step is not None:
            self.current_step = step

        self.update_timestamp()

    def get_runtime(self) -> float:
        """
        Возвращает общее время работы бота.

        Returns:
            Общее время работы (секунды)
        """
        return time.time() - self.start_time

    def get_average_time(self) -> Optional[float]:
        """
        Возвращает среднее время прохождения обучения.

        Returns:
            Среднее время (секунды) или None, если нет успешных прохождений
        """
        if self.success_count > 0:
            return self.total_time / self.success_count
        return None

    def get_success_rate(self) -> Optional[float]:
        """
        Возвращает процент успешных прохождений.

        Returns:
            Процент успешных прохождений (0-100) или None, если нет попыток
        """
        total_attempts = self.success_count + self.failure_count
        if total_attempts > 0:
            return (self.success_count / total_attempts) * 100
        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует статистику в словарь.

        Returns:
            Словарь со статистикой
        """
        return {
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'error_count': self.error_count,
            'completed_servers': self.completed_servers.copy(),
            'failed_servers': self.failed_servers.copy(),
            'server_history': self.server_history.copy(),
            'total_time': self.total_time,
            'runtime': self.get_runtime(),
            'avg_time': self.get_average_time(),
            'success_rate': self.get_success_rate(),
            'start_time': self.start_time,
            'last_update': self.last_update,
            'current_server': self.current_server,
            'current_season': self.current_season,
            'current_step': self.current_step
        }

    def from_dict(self, stats_dict: Dict[str, Any]) -> None:
        """
        Обновляет статистику из словаря.

        Args:
            stats_dict: Словарь со статистикой
        """
        if 'success_count' in stats_dict:
            self.success_count = stats_dict['success_count']

        if 'failure_count' in stats_dict:
            self.failure_count = stats_dict['failure_count']

        if 'error_count' in stats_dict:
            self.error_count = stats_dict['error_count']

        if 'completed_servers' in stats_dict:
            self.completed_servers = stats_dict['completed_servers'].copy()

        if 'failed_servers' in stats_dict:
            self.failed_servers = stats_dict['failed_servers'].copy()

        if 'server_history' in stats_dict:
            self.server_history = stats_dict['server_history'].copy()

        if 'total_time' in stats_dict:
            self.total_time = stats_dict['total_time']

        if 'start_time' in stats_dict:
            self.start_time = stats_dict['start_time']

        if 'last_update' in stats_dict:
            self.last_update = stats_dict['last_update']

        if 'current_server' in stats_dict:
            self.current_server = stats_dict['current_server']

        if 'current_season' in stats_dict:
            self.current_season = stats_dict['current_season']

        if 'current_step' in stats_dict:
            self.current_step = stats_dict['current_step']

    def save_to_file(self, filename: str = "statistics.json") -> bool:
        """
        Сохраняет статистику в файл.

        Args:
            filename: Имя файла для сохранения

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            stats_dict = self.to_dict()

            # Удаляем временные метки, которые нельзя сериализовать
            if 'start_time' in stats_dict:
                stats_dict['start_time_str'] = datetime.fromtimestamp(stats_dict['start_time']).strftime(
                    '%Y-%m-%d %H:%M:%S')
                del stats_dict['start_time']

            if 'last_update' in stats_dict:
                stats_dict['last_update_str'] = datetime.fromtimestamp(stats_dict['last_update']).strftime(
                    '%Y-%m-%d %H:%M:%S')
                del stats_dict['last_update']

            # Создаем папку, если ее нет
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats_dict, f, indent=4, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Ошибка при сохранении статистики: {e}")
            return False

    def load_from_file(self, filename: str = "statistics.json") -> bool:
        """
        Загружает статистику из файла.

        Args:
            filename: Имя файла для загрузки

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            if not os.path.exists(filename):
                return False

            with open(filename, 'r', encoding='utf-8') as f:
                stats_dict = json.load(f)

            # Преобразуем строковые временные метки обратно в числа
            if 'start_time_str' in stats_dict:
                stats_dict['start_time'] = datetime.strptime(stats_dict['start_time_str'],
                                                             '%Y-%m-%d %H:%M:%S').timestamp()
                del stats_dict['start_time_str']

            if 'last_update_str' in stats_dict:
                stats_dict['last_update'] = datetime.strptime(stats_dict['last_update_str'],
                                                              '%Y-%m-%d %H:%M:%S').timestamp()
                del stats_dict['last_update_str']

            self.from_dict(stats_dict)
            return True
        except Exception as e:
            print(f"Ошибка при загрузке статистики: {e}")
            return False

    def _get_season_for_server(self, server_number: int) -> str:
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