import subprocess
import logging
import time
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)


class ADB:
    """Класс для работы с ADB."""

    def __init__(self, device_id: Optional[str] = None):
        """
        Инициализация базового класса ADB.

        Args:
            device_id: Идентификатор устройства, если None - будет использовано первое доступное
        """
        self.device_id = device_id
        self.min_action_interval = 1.5  # Минимальный интервал между действиями (секунды)
        self.last_action_time = 0
        self._check_connection()

    def _check_connection(self) -> None:
        """Проверяет подключение к устройству и выбирает устройство, если не указано."""
        try:
            success, devices = self.execute_adb_command("devices")

            if not success:
                raise ConnectionError("Не удалось получить список устройств")

            if "List of devices attached" in devices and len(devices.strip().split('\n')) > 1:
                if self.device_id is None:
                    # Если ID устройства не указан, берем первое из списка
                    device_line = devices.strip().split('\n')[1]
                    self.device_id = device_line.split('\t')[0]
                    logger.info(f"Автоматически выбрано устройство: {self.device_id}")

                # Проверяем, что выбранное устройство доступно
                if self.device_id not in devices:
                    raise ConnectionError(f"Устройство {self.device_id} не найдено")

                logger.info(f"Подключение к устройству успешно установлено: {self.device_id}")
            else:
                raise ConnectionError("Не найдено подключенных устройств")
        except Exception as e:
            logger.error(f"Ошибка при подключении к устройству: {e}")
            raise

    def wait_for_interval(self) -> None:
        """Ожидает минимальный интервал между действиями."""
        current_time = time.time()
        time_since_last_action = current_time - self.last_action_time

        # Если не прошло достаточно времени с последнего действия, ждем
        if time_since_last_action < self.min_action_interval:
            sleep_time = self.min_action_interval - time_since_last_action
            logger.debug(f"Ожидание {sleep_time:.2f} сек. перед следующим действием")
            time.sleep(sleep_time)

    def execute_adb_command(self, command: str) -> Tuple[bool, str]:
        """
        Выполняет команду ADB.

        Args:
            command: Команда для выполнения (без префикса 'adb')

        Returns:
            Кортеж (успех, результат)
        """
        try:
            full_command = f"adb {'-s ' + self.device_id if self.device_id else ''} {command}"
            logger.debug(f"Выполнение команды: {full_command}")
            result = subprocess.check_output(full_command, shell=True, text=True, stderr=subprocess.STDOUT)
            return True, result.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка выполнения ADB команды: {e.output}")
            return False, e.output
        except Exception as e:
            logger.error(f"Неизвестная ошибка при выполнении команды ADB: {e}")
            return False, str(e)

    def get_screenshot(self) -> bytes:
        """
        Делает скриншот экрана и возвращает его в виде байтов.

        Returns:
            Скриншот в виде байтов
        """
        try:
            self.wait_for_interval()

            # Попробуем сначала создать директорию для скриншота, если её нет
            self.execute_adb_command("shell mkdir -p /sdcard/")

            # Проверим доступность устройства перед скриншотом
            success, output = self.execute_adb_command("shell echo 'Test connection'")
            if not success:
                raise Exception(f"Устройство не отвечает: {output}")

            # Сохраняем скриншот в файл на устройстве
            success, output = self.execute_adb_command("shell screencap -p /sdcard/screenshot.png")
            if not success:
                raise Exception(f"Не удалось сделать скриншот: {output}")

            # Получаем содержимое файла в виде байтов
            command = f"adb {'-s ' + self.device_id if self.device_id else ''} pull /sdcard/screenshot.png -"
            try:
                screenshot_bytes = subprocess.check_output(command, shell=True)
            except subprocess.CalledProcessError as e:
                raise Exception(f"Не удалось загрузить скриншот: {e.output if hasattr(e, 'output') else str(e)}")

            # Удаляем файл со скриншотом
            self.execute_adb_command("shell rm /sdcard/screenshot.png")

            self.last_action_time = time.time()
            return screenshot_bytes
        except Exception as e:
            logger.error(f"Ошибка при получении скриншота: {e}")
            raise

    def click(self, x: int, y: int) -> bool:
        """
        Выполняет клик по указанным координатам.

        Args:
            x: Координата X
            y: Координата Y

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            self.wait_for_interval()
            success, _ = self.execute_adb_command(f"shell input tap {x} {y}")
            logger.info(f"Клик по координатам: ({x}, {y})")
            self.last_action_time = time.time()
            return success
        except Exception as e:
            logger.error(f"Ошибка при выполнении клика: {e}")
            return False

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 500) -> bool:
        """
        Выполняет свайп от одних координат к другим.

        Args:
            start_x: Начальная координата X
            start_y: Начальная координата Y
            end_x: Конечная координата X
            end_y: Конечная координата Y
            duration_ms: Продолжительность свайпа в миллисекундах

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            self.wait_for_interval()
            success, _ = self.execute_adb_command(
                f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}")
            logger.info(f"Свайп от ({start_x}, {start_y}) к ({end_x}, {end_y})")
            self.last_action_time = time.time()
            return success
        except Exception as e:
            logger.error(f"Ошибка при выполнении свайпа: {e}")
            return False

    def press_key(self, key_code: int) -> bool:
        """
        Отправляет нажатие клавиши на устройство.

        Args:
            key_code: Код клавиши Android (например, 4 для BACK)

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            self.wait_for_interval()
            success, _ = self.execute_adb_command(f"shell input keyevent {key_code}")
            logger.info(f"Нажатие клавиши с кодом: {key_code}")
            self.last_action_time = time.time()
            return success
        except Exception as e:
            logger.error(f"Ошибка при нажатии клавиши: {e}")
            return False

    def press_esc(self) -> bool:
        """
        Отправляет нажатие клавиши ESC (эквивалент BACK в Android).

        Returns:
            True в случае успеха, False в случае ошибки
        """
        success = self.press_key(4)  # 4 - код клавиши BACK в Android
        if success:
            logger.info("Нажатие клавиши ESC (BACK)")
        return success

    def start_app(self, package_name: str, activity_name: Optional[str] = None) -> bool:
        """
        Запускает приложение на устройстве.

        Args:
            package_name: Имя пакета приложения
            activity_name: Имя активности (если нужно запустить конкретную)

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            self.wait_for_interval()

            if activity_name:
                success, _ = self.execute_adb_command(f"shell am start -n {package_name}/{activity_name}")
                logger.info(f"Запуск приложения: {package_name}/{activity_name}")
            else:
                success, _ = self.execute_adb_command(
                    f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
                logger.info(f"Запуск приложения: {package_name}")

            self.last_action_time = time.time()
            return success
        except Exception as e:
            logger.error(f"Ошибка при запуске приложения: {e}")
            return False

    def close_app(self, package_name: str) -> bool:
        """
        Закрывает приложение на устройстве.

        Args:
            package_name: Имя пакета приложения

        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            self.wait_for_interval()
            success, _ = self.execute_adb_command(f"shell am force-stop {package_name}")
            logger.info(f"Закрытие приложения: {package_name}")
            self.last_action_time = time.time()
            return success
        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {e}")
            return False