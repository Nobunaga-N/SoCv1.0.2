import time
import logging
import threading
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime

from src.core.emulator import Emulator
from src.core.recognition.image import ImageRecognition
from src.core.recognition.text import TextRecognition
from src.core.tutorial.step import TutorialStep
from src.core.tutorial.steps_factory import StepsFactory
from src.models.settings import BotSettings
from src.models.statistics import BotStatistics
from src.utils.helpers import get_season_for_server

logger = logging.getLogger(__name__)


class SeaConquestBot:
    """Основной класс бота для прохождения обучения в игре Sea of Conquest."""

    def __init__(self, settings: BotSettings, assets_path: Optional[str] = None):
        """
        Инициализация бота.

        Args:
            settings: Настройки бота
            assets_path: Путь к папке с изображениями для распознавания (если None, берется из настроек)
        """
        self.settings = settings
        self.statistics = BotStatistics()

        # Инициализация эмулятора
        self.emulator = Emulator(settings.device_id, settings.ldplayer_path)

        # Инициализация модулей распознавания
        self.assets_path = assets_path or settings.assets_path
        self.image_recognition = ImageRecognition(self.assets_path)
        self.text_recognition = TextRecognition(settings.tessdata_path)

        # Состояние бота
        self.running = False
        self.paused = False
        self._stop_event = threading.Event()

        # Текущий прогресс
        self.current_server = settings.start_server
        self.current_season = self._get_season_for_server(self.current_server)
        self.current_step_id = 0

        # Получаем шаги обучения
        self.tutorial_steps = StepsFactory.create_tutorial_steps()

        # Пакет и активность игры
        self.game_package = "com.seaofconquest.global"
        self.game_activity = "com.kingsgroup.mo.KGUnityPlayerActivity"

        # Добавляем обработчики для расширенных типов действий
        StepsFactory.add_extended_actions(self)

        logger.info(f"Бот инициализирован. Текущий сервер: {self.current_server}, сезон: {self.current_season}")

    def _get_season_for_server(self, server_number: int) -> str:
        """
        Определяет сезон для указанного номера сервера.

        Args:
            server_number: Номер сервера

        Returns:
            Название сезона
        """
        return get_season_for_server(server_number)

    def start(self) -> None:
        """Запускает бота в отдельном потоке."""
        if self.running:
            logger.warning("Бот уже запущен")
            return

        # Проверка подключения к эмулятору
        if not self.emulator.check_connection():
            logger.error("Не удалось подключиться к эмулятору. Бот не запущен.")
            return

        self.running = True
        self.paused = False
        self._stop_event.clear()

        # Обновляем время начала работы
        self.statistics.start_time = time.time()

        # Запускаем бота в отдельном потоке
        threading.Thread(target=self._run, daemon=True).start()

        logger.info(
            f"Бот запущен с настройками: start_server={self.settings.start_server}, "
            f"end_server={self.settings.end_server}, current_server={self.current_server}"
        )

    def stop(self) -> None:
        """Останавливает работу бота."""
        if not self.running:
            logger.warning("Бот не запущен")
            return

        logger.info("Остановка бота...")
        self._stop_event.set()
        self.running = False

    def pause(self) -> None:
        """Приостанавливает работу бота."""
        if not self.running:
            logger.warning("Нельзя приостановить незапущенного бота")
            return

        if self.paused:
            logger.warning("Бот уже приостановлен")
            return

        logger.info("Бот приостановлен")
        self.paused = True

    def resume(self) -> None:
        """Возобновляет работу бота после паузы."""
        if not self.running:
            logger.warning("Нельзя возобновить незапущенного бота")
            return

        if not self.paused:
            logger.warning("Бот не находится на паузе")
            return

        logger.info("Бот возобновлен")
        self.paused = False

    def _run(self) -> None:
        """Основной цикл работы бота."""
        try:
            recovery_attempts = 0
            max_recovery_attempts = 3

            while self.running and not self._stop_event.is_set():
                try:
                    # Если бот на паузе, ждем
                    if self.paused:
                        time.sleep(1)
                        continue

                    # Проверяем, нужно ли переходить к следующему серверу
                    if self.current_server < self.settings.end_server:
                        logger.info(f"Достигнут последний сервер {self.settings.end_server}, останавливаем бота")
                        self.running = False
                        break

                    # Обновляем текущий прогресс в статистике
                    self.statistics.set_current_progress(self.current_server, self.current_season)

                    logger.info(
                        f"Начинаем прохождение обучения на сервере {self.current_server} (сезон {self.current_season})"
                    )

                    # Запускаем цикл прохождения обучения
                    start_time = time.time()
                    tutorial_success = self._complete_tutorial()
                    tutorial_time = time.time() - start_time

                    if tutorial_success:
                        logger.info(
                            f"Обучение на сервере {self.current_server} успешно завершено за {tutorial_time:.1f} сек"
                        )
                        self.statistics.add_success(self.current_server, tutorial_time)
                        # Сбрасываем счетчик попыток восстановления
                        recovery_attempts = 0
                    else:
                        logger.error(f"Не удалось завершить обучение на сервере {self.current_server}")
                        self.statistics.add_failure(self.current_server, "Не удалось завершить обучение")

                    # Переходим к следующему серверу
                    self.current_server -= 1  # Серверы идут в убывающем порядке
                    if self.current_server < self.settings.end_server:
                        logger.info(f"Достигнут последний сервер {self.settings.end_server}, останавливаем бота")
                        self.running = False
                        break

                    self.current_season = self._get_season_for_server(self.current_server)

                except Exception as e:
                    # Пытаемся восстановиться после ошибки
                    if self._handle_error(e) and recovery_attempts < max_recovery_attempts:
                        recovery_attempts += 1
                        logger.info(f"Попытка восстановления {recovery_attempts}/{max_recovery_attempts}")
                        time.sleep(5)  # Пауза перед повторной попыткой
                    else:
                        if recovery_attempts >= max_recovery_attempts:
                            logger.error(
                                f"Превышено максимальное количество попыток восстановления ({max_recovery_attempts})"
                            )

                        # Если не удалось восстановиться, переходим к следующему серверу
                        logger.warning(f"Не удалось восстановиться после ошибки, переходим к следующему серверу")
                        self.statistics.add_failure(self.current_server, f"Ошибка: {str(e)}")
                        self.current_server -= 1
                        self.current_season = self._get_season_for_server(self.current_server)
                        recovery_attempts = 0

            logger.info("Бот остановлен")

        except Exception as e:
            logger.critical(f"Критическая ошибка в основном цикле бота: {e}", exc_info=True)
            self.running = False
            self.statistics.add_error(f"Критическая ошибка: {str(e)}")

    def _complete_tutorial(self) -> bool:
        """
        Выполняет прохождение всех шагов обучения для текущего сервера.

        Returns:
            True, если обучение успешно завершено, иначе False
        """
        try:
            # Перебираем шаги обучения
            current_step_index = 0
            while current_step_index < len(self.tutorial_steps):
                # Проверяем, не остановлен ли бот
                if self._stop_event.is_set() or not self.running:
                    logger.info("Прерывание прохождения обучения по требованию")
                    return False

                # Если бот на паузе, ждем
                if self.paused:
                    time.sleep(1)
                    continue

                step = self.tutorial_steps[current_step_index]
                logger.info(f"Выполняем шаг {step.step_id}: {step.description}")

                # Обновляем текущий шаг в статистике
                self.current_step_id = step.step_id
                self.statistics.set_current_progress(step=step.step_id)

                # Выполняем действие в зависимости от типа шага
                success, next_step = self._execute_step(step)

                if success:
                    logger.info(f"Шаг {step.step_id} успешно выполнен")

                    # Если указан конкретный следующий шаг, переходим к нему
                    if next_step is not None:
                        logger.info(f"Переход к шагу {next_step}")
                        # Находим индекс шага с указанным ID
                        for i, s in enumerate(self.tutorial_steps):
                            if s.step_id == next_step:
                                current_step_index = i
                                break
                    else:
                        # Иначе просто переходим к следующему шагу
                        current_step_index += 1
                else:
                    logger.error(f"Шаг {step.step_id} не удалось выполнить")
                    # В случае ошибки делаем еще несколько попыток
                    retry_count = step.get_param('retry_count', 3)

                    if retry_count > 0:
                        logger.info(
                            f"Повторная попытка выполнения шага {step.step_id} (осталось попыток: {retry_count})"
                        )
                        step.set_param('retry_count', retry_count - 1)
                        time.sleep(2)  # Небольшая пауза перед повторной попыткой
                    else:
                        logger.error(f"Исчерпаны все попытки для шага {step.step_id}, прерывание обучения")
                        return False

            # Успешно завершили все шаги
            logger.info("Обучение успешно завершено")
            return True

        except Exception as e:
            logger.error(f"Ошибка при прохождении обучения: {e}", exc_info=True)
            self.statistics.add_error(f"Ошибка в _complete_tutorial: {str(e)}")
            return False

    def _execute_step(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
        """
        Выполняет один шаг обучения.

        Args:
            step: Объект шага обучения

        Returns:
            Кортеж (успех, следующий_шаг), где следующий_шаг - ID следующего шага или None
        """
        try:
            # Анализируем тип действия
            action_type = step.action_type

            # Вызываем соответствующий обработчик
            method_name = f"_execute_{action_type}"
            if hasattr(self, method_name):
                handler = getattr(self, method_name)
                return handler(step)

            # Если обработчик не найден, логируем ошибку
            logger.error(f"Неизвестный тип действия: {action_type}")
            return False, None

        except Exception as e:
            logger.error(f"Ошибка при выполнении шага {step.step_id}: {e}", exc_info=True)
            return False, None

    def _execute_click(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
        """
        Выполняет клик по координатам.

        Args:
            step: Шаг обучения

        Returns:
            Кортеж (успех, следующий_шаг)
        """
        try:
            x = step.get_param('x')
            y = step.get_param('y')

            success = self.emulator.click(x, y)
            return success, None
        except Exception as e:
            logger.error(f"Ошибка при выполнении клика: {e}")
            return False, None

    def _execute_click_image(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
        """
        Находит и кликает по изображению.

        Args:
            step: Шаг обучения

        Returns:
            Кортеж (успех, следующий_шаг)
        """
        try:
            image_name = step.get_param('image_name')

            # Делаем скриншот
            screenshot_bytes = self.emulator.get_screenshot()
            screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

            success = self.image_recognition.find_and_click_template(self.emulator, screenshot, image_name)
            return success, None
        except Exception as e:
            logger.error(f"Ошибка при клике по изображению: {e}")
            return False, None

    def _execute_swipe(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
        """
        Выполняет свайп.

        Args:
            step: Шаг обучения

        Returns:
            Кортеж (успех, следующий_шаг)
        """
        try:
            start_x = step.get_param('start_x')
            start_y = step.get_param('start_y')
            end_x = step.get_param('end_x')
            end_y = step.get_param('end_y')
            duration_ms = step.get_param('duration_ms', 500)

            success = self.emulator.swipe(start_x, start_y, end_x, end_y, duration_ms)
            return success, None
        except Exception as e:
            logger.error(f"Ошибка при выполнении свайпа: {e}")
            return False, None

    def _execute_wait(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
        """
        Ожидает указанное время.

        Args:
            step: Шаг обучения

        Returns:
            Кортеж (успех, следующий_шаг)
        """
        try:
            seconds = step.get_param('seconds')

            logger.info(f"Ожидание {seconds} сек.")
            time.sleep(seconds)
            return True, None
        except Exception as e:
            logger.error(f"Ошибка при ожидании: {e}")
            return False, None

    def _execute_start_app(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
        """
        Запускает приложение.

        Args:
            step: Шаг обучения

        Returns:
            Кортеж (успех, следующий_шаг)
        """
        try:
            package_name = step.get_param('package_name')
            activity_name = step.get_param('activity_name')

            success = self.emulator.start_app(package_name, activity_name)
            return success, None
        except Exception as e:
            logger.error(f"Ошибка при запуске приложения: {e}")
            return False, None

    def _execute_close_app(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
        """
        Закрывает приложение.

        Args:
            step: Шаг обучения

        Returns:
            Кортеж (успех, следующий_шаг)
        """
        try:
            package_name = step.get_param('package_name')

            success = self.emulator.close_app(package_name)
            return success, None
        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {e}")
            return False, None

    def restart_game(self) -> bool:
        """
        Перезапускает игру.

        Returns:
            True в случае успеха, False в случае неудачи
        """
        try:
            logger.info("Закрытие игры")
            self.emulator.close_app(self.game_package)
            time.sleep(3)

            logger.info("Запуск игры")
            self.emulator.start_app(self.game_package, self.game_activity)

            # Ждем загрузки игры
            time.sleep(10)

            return True
        except Exception as e:
            logger.error(f"Ошибка при перезапуске игры: {e}")
            return False

    def restart_emulator(self) -> bool:
        """
        Перезапускает эмулятор.

        Returns:
            True в случае успеха, False в случае неудачи
        """
        try:
            logger.info("Перезапуск эмулятора")
            if self.emulator.restart_emulator():
                logger.info("Эмулятор успешно перезапущен")
                return True
            else:
                logger.error("Не удалось перезапустить эмулятор")
                return False
        except Exception as e:
            logger.error(f"Ошибка при перезапуске эмулятора: {e}")
            return False

    def _handle_error(self, e: Exception) -> bool:
        """
        Обрабатывает ошибку и пытается восстановить работу бота.

        Args:
            e: Исключение

        Returns:
            True, если удалось восстановиться, иначе False
        """
        try:
            logger.error(f"Произошла ошибка: {e}", exc_info=True)
            self.statistics.add_error(str(e))

            # Проверяем, запущено ли приложение
            try:
                screenshot_bytes = self.emulator.get_screenshot()
                if screenshot_bytes:
                    logger.info("Эмулятор отвечает, пробуем продолжить работу")
                    return True
            except:
                logger.warning("Не удалось получить скриншот, возможно, проблемы с эмулятором")

            # Пробуем перезапустить приложение
            try:
                if self.restart_game():
                    logger.info("Игра перезапущена после ошибки")
                    return True
            except:
                logger.warning("Не удалось перезапустить игру")

            # В крайнем случае, пробуем перезапустить эмулятор
            try:
                if self.restart_emulator():
                    logger.info("Эмулятор перезапущен после ошибки")
                    # Перезапускаем игру после перезапуска эмулятора
                    time.sleep(10)  # Даем время эмулятору загрузиться
                    if self.restart_game():
                        return True
            except:
                logger.error("Не удалось перезапустить эмулятор")

            return False
        except Exception as recovery_error:
            logger.error(f"Ошибка при попытке восстановления: {recovery_error}", exc_info=True)
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Возвращает текущую статистику работы бота.

        Returns:
            Словарь с данными статистики
        """
        return self.statistics.to_dict()