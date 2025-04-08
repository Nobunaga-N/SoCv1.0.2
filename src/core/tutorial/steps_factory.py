import logging
import time
from typing import List, Tuple, Optional, Dict, Any, Callable
import numpy as np

from src.core.tutorial.step import TutorialStep
from src.core.tutorial.steps_data import TUTORIAL_STEPS_DATA

logger = logging.getLogger(__name__)


class StepsFactory:
    """Фабрика для создания и инициализации шагов обучения."""

    @staticmethod
    def create_tutorial_steps() -> List[TutorialStep]:
        """
        Создает полный список шагов обучения.

        Returns:
            Список шагов обучения
        """
        steps = []

        # Создаем шаги из определенных данных
        for step_data in TUTORIAL_STEPS_DATA:
            step_id = step_data.pop("step_id")
            description = step_data.pop("description")
            action_type = step_data.pop("action_type")

            # Создаем шаг обучения с оставшимися параметрами
            step = TutorialStep(step_id, description, action_type, **step_data)
            steps.append(step)

        logger.info(f"Создано {len(steps)} шагов обучения")
        return steps

    @staticmethod
    def add_extended_actions(bot) -> None:
        """
        Добавляет обработчики для расширенных типов действий в бота.

        Args:
            bot: Экземпляр бота
        """
        # Добавляем обработчики для расширенных типов действий
        StepsFactory._add_delayed_click_handler(bot)
        StepsFactory._add_repeat_click_until_image_handler(bot)
        StepsFactory._add_find_and_click_or_repeat_handler(bot)
        StepsFactory._add_find_and_click_multiple_handler(bot)
        StepsFactory._add_wait_for_image_handler(bot)
        StepsFactory._add_wait_for_image_with_esc_handler(bot)
        StepsFactory._add_complex_swipe_handler(bot)
        StepsFactory._add_select_season_handler(bot)
        StepsFactory._add_select_server_handler(bot)

        logger.info("Добавлены обработчики для расширенных типов действий")

    @staticmethod
    def _add_delayed_click_handler(bot) -> None:
        """
        Добавляет обработчик для действия delayed_click.

        Args:
            bot: Экземпляр бота
        """

        def delayed_click(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Выполняет клик по координатам с предварительной задержкой.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                delay_seconds = step.get_param('delay_seconds', 0)

                if delay_seconds > 0:
                    logger.info(f"Ожидание {delay_seconds} сек. перед кликом")
                    time.sleep(delay_seconds)

                success = self.emulator.click(step.get_param('x'), step.get_param('y'))
                return success, None
            except Exception as e:
                logger.error(f"Ошибка при выполнении задержанного клика: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_delayed_click = delayed_click.__get__(bot)

    @staticmethod
    def _add_repeat_click_until_image_handler(bot) -> None:
        """
        Добавляет обработчик для действия repeat_click_until_image.

        Args:
            bot: Экземпляр бота
        """

        def repeat_click_until_image(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Многократно кликает по координатам, пока не обнаружит целевое изображение.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                x = step.get_param('x')
                y = step.get_param('y')
                interval = step.get_param('interval_seconds', 1.5)
                max_attempts = step.get_param('max_attempts', 0)  # 0 - без ограничения
                target_image = step.get_param('target_image')
                click_on_image = step.get_param('click_on_image', False)

                attempt = 0

                while max_attempts == 0 or attempt < max_attempts:
                    # Делаем скриншот
                    screenshot_bytes = self.emulator.get_screenshot()
                    screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                    # Ищем целевое изображение
                    template_rect = self.image_recognition.find_template(screenshot, target_image)

                    if template_rect:
                        logger.info(f"Найдено изображение {target_image} после {attempt + 1} попыток")

                        if click_on_image:
                            # Кликаем по найденному изображению
                            x, y, w, h = template_rect
                            center_x = x + w // 2
                            center_y = y + h // 2
                            self.emulator.click(center_x, center_y)
                            logger.info(
                                f"Клик по найденному изображению {target_image} в позиции ({center_x}, {center_y})")

                        return True, None

                    # Кликаем по заданным координатам
                    self.emulator.click(x, y)
                    logger.debug(f"Клик по координатам ({x}, {y}), попытка {attempt + 1}")

                    # Увеличиваем счетчик попыток
                    attempt += 1

                    # Ждем указанный интервал
                    time.sleep(interval)

                logger.warning(f"Не удалось найти изображение {target_image} после {attempt} попыток")
                return False, None
            except Exception as e:
                logger.error(f"Ошибка при выполнении повторяющегося клика: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_repeat_click_until_image = repeat_click_until_image.__get__(bot)

    @staticmethod
    def _add_find_and_click_or_repeat_handler(bot) -> None:
        """
        Добавляет обработчик для действия find_and_click_or_repeat.

        Args:
            bot: Экземпляр бота
        """

        def find_and_click_or_repeat(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Находит и кликает по изображению, если не находит - выполняет случайный клик.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                max_attempts = step.get_param('max_attempts', 5)
                wait_time = step.get_param('wait_between_attempts', 2)
                image_name = step.get_param('image_name')

                screenshot_bytes = self.emulator.get_screenshot()
                screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                for attempt in range(max_attempts):
                    # Ищем изображение
                    template_rect = self.image_recognition.find_template(screenshot, image_name)

                    if template_rect:
                        # Кликаем по найденному изображению
                        x, y, w, h = template_rect
                        center_x = x + w // 2
                        center_y = y + h // 2
                        self.emulator.click(center_x, center_y)
                        logger.info(f"Клик по найденному изображению {image_name} в позиции ({center_x}, {center_y})")
                        return True, None

                    # Если не нашли изображение и разрешено кликать в случайной точке
                    if step.get_param('click_random_if_not_found', False):
                        # Генерируем случайные координаты в указанном радиусе
                        import random
                        center_x = step.get_param('random_center_x', 640)
                        center_y = step.get_param('random_center_y', 360)
                        radius = step.get_param('random_radius', 100)

                        angle = random.uniform(0, 2 * 3.14159)
                        distance = random.uniform(0, radius)

                        x = int(center_x + distance * np.cos(angle))
                        y = int(center_y + distance * np.sin(angle))

                        self.emulator.click(x, y)
                        logger.info(f"Случайный клик в позиции ({x}, {y})")

                    # Делаем новый скриншот
                    time.sleep(wait_time)
                    screenshot_bytes = self.emulator.get_screenshot()
                    screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                logger.warning(f"Не удалось найти изображение {image_name} после {max_attempts} попыток")
                return False, None
            except Exception as e:
                logger.error(f"Ошибка при выполнении find_and_click_or_repeat: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_find_and_click_or_repeat = find_and_click_or_repeat.__get__(bot)

    @staticmethod
    def _add_find_and_click_multiple_handler(bot) -> None:
        """
        Добавляет обработчик для действия find_and_click_multiple.

        Args:
            bot: Экземпляр бота
        """

        def find_and_click_multiple(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Ищет и кликает по одному из нескольких изображений.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                images = step.get_param('images', [])
                priority_image = step.get_param('priority_image')
                next_step_on_priority = step.get_param('next_step_on_priority')

                screenshot_bytes = self.emulator.get_screenshot()
                screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                for image_name in images:
                    # Ищем изображение
                    template_rect = self.image_recognition.find_template(screenshot, image_name)

                    if template_rect:
                        # Кликаем по найденному изображению
                        x, y, w, h = template_rect
                        center_x = x + w // 2
                        center_y = y + h // 2
                        self.emulator.click(center_x, center_y)
                        logger.info(f"Клик по найденному изображению {image_name} в позиции ({center_x}, {center_y})")

                        # Если нашли приоритетное изображение, возвращаем следующий шаг
                        if image_name == priority_image and next_step_on_priority is not None:
                            return True, next_step_on_priority
                        return True, None

                logger.warning(f"Не удалось найти ни одно изображение из списка: {images}")
                return False, None
            except Exception as e:
                logger.error(f"Ошибка при выполнении find_and_click_multiple: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_find_and_click_multiple = find_and_click_multiple.__get__(bot)

    @staticmethod
    def _add_wait_for_image_handler(bot) -> None:
        """
        Добавляет обработчик для действия wait_for_image.

        Args:
            bot: Экземпляр бота
        """

        def wait_for_image(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Ожидает появления изображения на экране.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                timeout = step.get_param('timeout', 60)
                check_interval = step.get_param('check_interval', 2)
                image_name = step.get_param('image_name')

                start_time = time.time()

                while time.time() - start_time < timeout:
                    # Делаем скриншот
                    screenshot_bytes = self.emulator.get_screenshot()
                    screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                    # Ищем изображение
                    template_rect = self.image_recognition.find_template(screenshot, image_name)

                    if template_rect:
                        logger.info(f"Найдено изображение {image_name} через {time.time() - start_time:.1f} сек")
                        return True, None

                    time.sleep(check_interval)

                logger.warning(f"Не удалось дождаться изображения {image_name} за {timeout} сек")
                return False, None
            except Exception as e:
                logger.error(f"Ошибка при выполнении wait_for_image: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_wait_for_image = wait_for_image.__get__(bot)

    @staticmethod
    def _add_wait_for_image_with_esc_handler(bot) -> None:
        """
        Добавляет обработчик для действия wait_for_image_with_esc.

        Args:
            bot: Экземпляр бота
        """

        def wait_for_image_with_esc(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Ожидает появления изображения на экране, периодически нажимая ESC.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                timeout = step.get_param('timeout', 120)
                check_interval = step.get_param('check_interval', 5)
                esc_interval = step.get_param('esc_interval', 10)
                image_name = step.get_param('image_name')

                start_time = time.time()
                last_esc_time = 0

                while time.time() - start_time < timeout:
                    # Делаем скриншот
                    screenshot_bytes = self.emulator.get_screenshot()
                    screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                    # Ищем изображение
                    template_rect = self.image_recognition.find_template(screenshot, image_name)

                    if template_rect:
                        logger.info(f"Найдено изображение {image_name} через {time.time() - start_time:.1f} сек")
                        return True, None

                    # Нажимаем ESC с заданным интервалом
                    current_time = time.time()
                    if current_time - last_esc_time >= esc_interval:
                        logger.info("Нажатие ESC для закрытия рекламы")
                        self.emulator.press_esc()
                        last_esc_time = current_time

                    time.sleep(check_interval)

                logger.warning(f"Не удалось дождаться изображения {image_name} за {timeout} сек")
                return False, None
            except Exception as e:
                logger.error(f"Ошибка при выполнении wait_for_image_with_esc: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_wait_for_image_with_esc = wait_for_image_with_esc.__get__(bot)

    @staticmethod
    def _add_complex_swipe_handler(bot) -> None:
        """
        Добавляет обработчик для действия complex_swipe.

        Args:
            bot: Экземпляр бота
        """

        def complex_swipe(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Выполняет сложный свайп через несколько точек.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                points = step.get_param('points', [])
                duration_ms = step.get_param('duration_ms', 1000)

                if len(points) < 2:
                    logger.error("Для свайпа требуется минимум 2 точки")
                    return False, None

                success = self.emulator.complex_swipe(points, duration_ms)
                return success, None
            except Exception as e:
                logger.error(f"Ошибка при выполнении complex_swipe: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_complex_swipe = complex_swipe.__get__(bot)

    @staticmethod
    def _add_select_season_handler(bot) -> None:
        """
        Добавляет обработчик для действия select_season.

        Args:
            bot: Экземпляр бота
        """

        def select_season(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Выбирает нужный сезон.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            from src.core.tutorial.steps_data import VISIBLE_SEASONS, HIDDEN_SEASONS

            try:
                # Получаем текущий сезон из состояния бота
                target_season = self.current_season

                # Делаем скриншот
                screenshot_bytes = self.emulator.get_screenshot()
                screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                # Проверяем, видимый ли это сезон
                if target_season in HIDDEN_SEASONS:
                    # Если сезон скрыт, делаем скролл вниз
                    logger.info(f"Сезон {target_season} может быть скрыт, выполняем скролл")
                    self.emulator.swipe(257, 353, 254, 187, 800)
                    time.sleep(2)  # Ждем завершения скролла

                    # Делаем новый скриншот
                    screenshot_bytes = self.emulator.get_screenshot()
                    screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                # Используем text_recognition для поиска сезона
                season_coords = self.text_recognition.find_season(screenshot, target_season)

                if season_coords:
                    # Нашли сезон, кликаем по нему
                    success = self.emulator.click(season_coords[0], season_coords[1])
                    logger.info(f"Найден и выбран сезон: {target_season}")
                    return success, None

                # Если сезон не найден, пробуем найти по шаблону
                season_template = f"season_{target_season.replace(' ', '_').lower()}"
                if self.image_recognition.find_and_click_template(self.emulator, screenshot, season_template):
                    logger.info(f"Найден и выбран сезон по шаблону: {target_season}")
                    return True, None

                logger.error(f"Не удалось найти сезон: {target_season}")
                return False, None
            except Exception as e:
                logger.error(f"Ошибка при выборе сезона: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_select_season = select_season.__get__(bot)

    @staticmethod
    def _add_select_server_handler(bot) -> None:
        """
        Добавляет обработчик для действия select_server.

        Args:
            bot: Экземпляр бота
        """

        def select_server(self, step: TutorialStep) -> Tuple[bool, Optional[int]]:
            """
            Выбирает нужный сервер.

            Args:
                step: Шаг обучения

            Returns:
                Кортеж (успех, следующий_шаг)
            """
            try:
                # Получаем текущий сервер из состояния бота
                target_server = self.current_server

                # Максимальное количество попыток скролла
                max_scroll_attempts = 20

                for scroll_attempt in range(max_scroll_attempts):
                    # Делаем скриншот
                    screenshot_bytes = self.emulator.get_screenshot()
                    screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)

                    # Используем text_recognition для поиска сервера
                    server_coords = self.text_recognition.find_specific_server(screenshot, target_server)

                    if server_coords:
                        # Нашли сервер, кликаем по нему
                        success = self.emulator.click(server_coords[0], server_coords[1])
                        logger.info(f"Найден и выбран сервер: {target_server}")
                        return success, None

                    # Если сервер не найден, делаем скролл вниз
                    logger.debug(
                        f"Сервер {target_server} не найден на экране, выполняем скролл (попытка {scroll_attempt + 1})")
                    self.emulator.swipe(778, 567, 778, 130, 800)
                    time.sleep(1.5)  # Ждем завершения скролла

                # Если после всех попыток сервер не найден, ищем следующий доступный
                logger.warning(f"Сервер {target_server} не найден после {max_scroll_attempts} попыток скролла")
                logger.info("Возможно, сервер недоступен или заполнен. Ищем следующий доступный сервер")

                # Возвращаемся в начало списка серверов
                for _ in range(5):
                    self.emulator.swipe(778, 130, 778, 567, 800)
                    time.sleep(1)

                # Ищем все доступные серверы
                screenshot_bytes = self.emulator.get_screenshot()
                screenshot = self.image_recognition.bytes_to_cv2_image(screenshot_bytes)
                server_numbers = self.text_recognition.find_server_numbers(screenshot)

                if server_numbers:
                    # Сортируем серверы по номерам (от большего к меньшему)
                    server_numbers.sort(key=lambda x: x[0], reverse=True)

                    # Ищем первый доступный сервер, номер которого меньше целевого
                    for server_number, coords in server_numbers:
                        if server_number < target_server:
                            success = self.emulator.click(coords[0], coords[1])
                            logger.info(
                                f"Сервер {target_server} недоступен, выбран ближайший доступный сервер: {server_number}")
                            # Обновляем текущий сервер
                            self.current_server = server_number
                            return success, None

                logger.error(f"Не удалось найти ни целевой сервер {target_server}, ни альтернативный")
                return False, None
            except Exception as e:
                logger.error(f"Ошибка при выборе сервера: {e}")
                return False, None

        # Добавляем метод в экземпляр бота
        bot._execute_select_server = select_server.__get__(bot)