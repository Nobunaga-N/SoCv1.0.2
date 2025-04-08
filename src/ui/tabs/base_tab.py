from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
import logging

from src.ui.ui_factory import UIFactory


class BaseTab(QWidget):
    """Базовый класс для вкладок интерфейса."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui_factory = UIFactory()
        self.logger = logging.getLogger(self.__class__.__name__)

        self._init_ui()

    def _init_ui(self):
        """
        Инициализирует UI компоненты.
        Должен быть переопределен в дочерних классах.
        """
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

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