import logging
from typing import Optional

from src.core.bot import SeaConquestBot
from src.models.settings import BotSettings
from src.utils.helpers import check_adb_installed, check_emulator_running

logger = logging.getLogger(__name__)


class BotFactory:
    """Фабрика для создания экземпляров бота."""

    @staticmethod
    def create_bot(settings: BotSettings) -> Optional[SeaConquestBot]:
        """
        Создает и возвращает экземпляр бота на основе настроек.

        Args:
            settings: Настройки бота

        Returns:
            Экземпляр бота или None, если создание не удалось
        """
        try:
            # Проверяем наличие необходимых компонентов
            if not check_adb_installed():
                logger.error("ADB не установлен. Установите Android Debug Bridge.")
                return None

            if not check_emulator_running():
                logger.warning("Эмулятор не запущен. Запустите эмулятор перед запуском бота.")
                return None

            # Создаем экземпляр бота
            bot = SeaConquestBot(settings)
            return bot
        except Exception as e:
            logger.error(f"Ошибка при создании бота: {e}", exc_info=True)
            return None