import os
import re
import logging
import subprocess
import time
from typing import List, Tuple, Optional, Dict

logger = logging.getLogger(__name__)


class LDPlayer:
    """Класс для работы с эмулятором LDPlayer."""

    def __init__(self, ldplayer_path: Optional[str] = None):
        """
        Инициализация объекта для работы с LDPlayer.

        Args:
            ldplayer_path: Путь к директории LDPlayer (если None, будет найден автоматически)
        """
        self.ldplayer_path = ldplayer_path or self._find_ldplayer_path()
        self.ldconsole_path = None

        if self.ldplayer_path:
            self.ldconsole_path = os.path.join(self.ldplayer_path, "ldconsole.exe")
            if not os.path.exists(self.ldconsole_path):
                logger.error(f"Не найден исполняемый файл ldconsole.exe по пути: {self.ldconsole_path}")
                self.ldconsole_path = None

    def _find_ldplayer_path(self) -> Optional[str]:
        """
        Автоматический поиск пути к LDPlayer.

        Returns:
            Путь к директории LDPlayer или None, если не найден
        """
        # Типичные пути установки LDPlayer
        possible_paths = [
            "C:\\LDPlayer\\LDPlayer9",
            "C:\\LDPlayer9",
            "C:\\Program Files\\LDPlayer\\LDPlayer9",
            "C:\\Program Files (x86)\\LDPlayer\\LDPlayer9",
            os.path.expanduser("~\\LDPlayer\\LDPlayer9"),
            "D:\\LDPlayer\\LDPlayer9",
        ]

        # Проверяем пути
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "ldconsole.exe")):
                logger.info(f"Найден LDPlayer по пути: {path}")
                return path

        # Если не нашли по известным путям, попробуем поискать через реестр Windows
        try:
            import winreg
            keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\LDPlayer\LDPlayer9"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\LDPlayer\LDPlayer9"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\LDPlayer\LDPlayer9"),
            ]

            for hkey, key_path in keys:
                try:
                    with winreg.OpenKey(hkey, key_path) as key:
                        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                        if os.path.exists(install_path) and os.path.exists(os.path.join(install_path, "ldconsole.exe")):
                            logger.info(f"Найден LDPlayer через реестр по пути: {install_path}")
                            return install_path
                except (WindowsError, OSError):
                    continue
        except ImportError:
            logger.debug("Модуль winreg недоступен, поиск через реестр невозможен")

        logger.error("Не удалось найти путь к LDPlayer")
        return None

    def is_available(self) -> bool:
        """
        Проверяет, доступен ли LDPlayer для управления.

        Returns:
            True, если LDPlayer доступен, иначе False
        """
        return self.ldconsole_path is not None and os.path.exists(self.ldconsole_path)

    def _run_ldconsole_command(self, command: str) -> Tuple[bool, str]:
        """
        Выполняет команду ldconsole.

        Args:
            command: Команда для выполнения

        Returns:
            Кортеж (успех, результат)
        """
        if not self.is_available():
            return False, "LDPlayer недоступен"

        try:
            full_command = f'"{self.ldconsole_path}" {command}'
            logger.debug(f"Выполнение команды: {full_command}")
            result = subprocess.check_output(full_command, shell=True, text=True, stderr=subprocess.STDOUT)
            return True, result.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка выполнения команды ldconsole: {e.output}")
            return False, e.output
        except Exception as e:
            logger.error(f"Неизвестная ошибка при выполнении команды ldconsole: {e}")
            return False, str(e)

    def list_emulators(self) -> List[Dict[str, str]]:
        """
        Получает список настроенных эмуляторов.

        Returns:
            Список словарей с информацией об эмуляторах
        """
        success, result = self._run_ldconsole_command("list")

        if not success:
            logger.error("Не удалось получить список эмуляторов")
            return []

        emulators = []
        lines = result.strip().split('\n')

        for line in lines:
            if not line.strip():
                continue

            # Парсим строку с информацией об эмуляторе
            parts = line.split(',')
            if len(parts) >= 2:
                emulator = {
                    'index': parts[0],
                    'name': parts[1],
                    'status': 'running' if self.is_running(parts[0]) else 'stopped'
                }
                emulators.append(emulator)

        return emulators

    def is_running(self, index: str) -> bool:
        """
        Проверяет, запущен ли эмулятор с указанным индексом.

        Args:
            index: Индекс эмулятора

        Returns:
            True, если эмулятор запущен, иначе False
        """
        success, result = self._run_ldconsole_command(f"isrunning --index {index}")

        if not success:
            return False

        return "running" in result.lower()

    def launch(self, index: str = "0") -> bool:
        """
        Запускает эмулятор с указанным индексом.

        Args:
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            True, если эмулятор успешно запущен, иначе False
        """
        if self.is_running(index):
            logger.info(f"Эмулятор с индексом {index} уже запущен")
            return True

        logger.info(f"Запуск эмулятора с индексом {index}")
        success, _ = self._run_ldconsole_command(f"launch --index {index}")

        if success:
            # Ждем запуска эмулятора
            for _ in range(60):  # Ждем до 60 секунд
                if self.is_running(index):
                    logger.info(f"Эмулятор с индексом {index} успешно запущен")
                    return True
                time.sleep(1)

            logger.warning(f"Эмулятор с индексом {index} запущен, но его статус не определён")
            return False
        else:
            logger.error(f"Не удалось запустить эмулятор с индексом {index}")
            return False

    def quit(self, index: str = "0") -> bool:
        """
        Закрывает эмулятор с указанным индексом.

        Args:
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            True, если эмулятор успешно закрыт, иначе False
        """
        if not self.is_running(index):
            logger.info(f"Эмулятор с индексом {index} уже остановлен")
            return True

        logger.info(f"Закрытие эмулятора с индексом {index}")
        success, _ = self._run_ldconsole_command(f"quit --index {index}")

        if success:
            # Ждем завершения работы эмулятора
            for _ in range(30):  # Ждем до 30 секунд
                if not self.is_running(index):
                    logger.info(f"Эмулятор с индексом {index} успешно закрыт")
                    return True
                time.sleep(1)

            logger.warning(f"Эмулятор с индексом {index} не закрылся за отведенное время")
            return False
        else:
            logger.error(f"Не удалось закрыть эмулятор с индексом {index}")
            return False

    def reboot(self, index: str = "0") -> bool:
        """
        Перезапускает эмулятор с указанным индексом.

        Args:
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            True, если эмулятор успешно перезапущен, иначе False
        """
        # Сначала закрываем эмулятор
        if not self.quit(index):
            logger.error(f"Не удалось закрыть эмулятор с индексом {index} для перезапуска")
            return False

        # Затем запускаем его снова
        if not self.launch(index):
            logger.error(f"Не удалось запустить эмулятор с индексом {index} после закрытия")
            return False

        logger.info(f"Эмулятор с индексом {index} успешно перезапущен")
        return True

    def get_device_id(self, index: str = "0") -> Optional[str]:
        """
        Получает ADB device ID для указанного эмулятора.

        Args:
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            ADB device ID или None, если не удалось получить
        """
        if not self.is_running(index):
            logger.error(f"Эмулятор с индексом {index} не запущен")
            return None

        try:
            # Получаем список устройств через ADB
            result = subprocess.check_output("adb devices", shell=True, text=True)

            # Ищем устройства, связанные с LDPlayer
            lines = result.strip().split('\n')[1:]  # Пропускаем заголовок

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split('\t')
                if len(parts) >= 2 and parts[1] == 'device':
                    device_id = parts[0]
                    # Проверяем, принадлежит ли устройство LDPlayer по формату ID
                    if re.match(r'emulator-\d+', device_id) or 'localhost' in device_id:
                        logger.info(f"Найден ADB device ID для эмулятора с индексом {index}: {device_id}")
                        return device_id

            logger.error(f"Не удалось найти ADB device ID для эмулятора с индексом {index}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении ADB device ID: {e}")
            return None

    def install_app(self, apk_path: str, index: str = "0") -> bool:
        """
        Устанавливает приложение на эмулятор.

        Args:
            apk_path: Путь к APK файлу
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            True, если приложение успешно установлено, иначе False
        """
        if not os.path.exists(apk_path):
            logger.error(f"APK файл не найден: {apk_path}")
            return False

        if not self.is_running(index):
            logger.error(f"Эмулятор с индексом {index} не запущен")
            return False

        logger.info(f"Установка приложения {apk_path} на эмулятор с индексом {index}")
        success, _ = self._run_ldconsole_command(f"installapp --index {index} --filename \"{apk_path}\"")

        return success

    def is_app_installed(self, package_name: str, index: str = "0") -> bool:
        """
        Проверяет, установлено ли приложение на эмулятор.

        Args:
            package_name: Имя пакета приложения
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            True, если приложение установлено, иначе False
        """
        if not self.is_running(index):
            logger.error(f"Эмулятор с индексом {index} не запущен")
            return False

        device_id = self.get_device_id(index)
        if not device_id:
            return False

        try:
            # Формируем команду ADB
            cmd = f"adb -s {device_id} shell pm list packages | grep {package_name}"

            # Выполняем команду
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

            # Проверяем результат
            return package_name in result.stdout
        except Exception as e:
            logger.error(f"Ошибка при проверке установки приложения: {e}")
            return False

    def set_prop(self, key: str, value: str, index: str = "0") -> bool:
        """
        Устанавливает свойство эмулятора.

        Args:
            key: Ключ свойства
            value: Значение свойства
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            True, если свойство успешно установлено, иначе False
        """
        logger.info(f"Установка свойства {key}={value} для эмулятора с индексом {index}")
        success, _ = self._run_ldconsole_command(f"setprop --index {index} --key {key} --value {value}")
        return success

    def modify_resolution(self, width: int, height: int, dpi: int = 240, index: str = "0") -> bool:
        """
        Изменяет разрешение эмулятора.

        Args:
            width: Ширина экрана
            height: Высота экрана
            dpi: DPI экрана
            index: Индекс эмулятора (по умолчанию "0")

        Returns:
            True, если разрешение успешно изменено, иначе False
        """
        logger.info(f"Изменение разрешения эмулятора с индексом {index} на {width}x{height}, DPI={dpi}")
        success, _ = self._run_ldconsole_command(
            f"modify --index {index} --resolution {width},{height},{dpi}"
        )
        return success