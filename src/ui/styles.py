from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt


class Styles:
    """Класс для хранения и применения стилей приложения."""

    @staticmethod
    def get_dark_palette():
        """Создает темную палитру цветов."""
        palette = QPalette()

        # Основные цвета
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        return palette

    @staticmethod
    def get_light_palette():
        """Создает светлую палитру цветов."""
        palette = QPalette()

        # Основные цвета
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 233, 233))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        return palette

    @staticmethod
    def get_stylesheets():
        """Возвращает словарь со стилями для разных компонентов."""
        return {
            'main_window': """
                QMainWindow {
                    border: 1px solid #555;
                }
            """,
            'push_button': """
                QPushButton {
                    background-color: #2a82da;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #3a92ea;
                }
                QPushButton:pressed {
                    background-color: #1a72ca;
                }
                QPushButton:disabled {
                    background-color: #888;
                    color: #ccc;
                }
            """,
            'start_button': """
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #3edc81;
                }
                QPushButton:pressed {
                    background-color: #1ebc61;
                }
                QPushButton:disabled {
                    background-color: #888;
                    color: #ccc;
                }
            """,
            'stop_button': """
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #f75c4c;
                }
                QPushButton:pressed {
                    background-color: #d73c2c;
                }
                QPushButton:disabled {
                    background-color: #888;
                    color: #ccc;
                }
            """,
            'group_box': """
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                }
            """,
            'text_edit': """
                QTextEdit {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px;
                }
            """,
            'tab_widget': """
                QTabWidget::pane {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QTabBar::tab {
                    background-color: #444;
                    color: white;
                    border: 1px solid #555;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 5px 15px;
                }
                QTabBar::tab:selected {
                    background-color: #2a82da;
                }
                QTabBar::tab:hover {
                    background-color: #555;
                }
            """,
            'spinbox': """
                QSpinBox {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 2px;
                }
            """,
            'combobox': """
                QComboBox {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 2px 5px;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #555;
                }
            """,
            'table': """
                QTableWidget {
                    border: 1px solid #555;
                    border-radius: 4px;
                    gridline-color: #555;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QHeaderView::section {
                    background-color: #444;
                    color: white;
                    padding: 5px;
                    border: 1px solid #555;
                }
            """,
            'scrollbar': """
                QScrollBar:vertical {
                    border: none;
                    background-color: #444;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #666;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    border: none;
                    background-color: #444;
                    height: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #666;
                    min-width: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
            """
        }

    @staticmethod
    def apply_dark_theme(app):
        """Применяет темную тему к приложению."""
        app.setPalette(Styles.get_dark_palette())

        # Применяем стили к компонентам
        stylesheets = Styles.get_stylesheets()

        for key, style in stylesheets.items():
            if key == 'main_window':
                continue  # Пропускаем стиль главного окна, применим его отдельно

            app.setStyleSheet(app.styleSheet() + style)

    @staticmethod
    def apply_light_theme(app):
        """Применяет светлую тему к приложению."""
        app.setPalette(Styles.get_light_palette())

        # Здесь можно настроить светлые стили для компонентов
        # В базовой реализации просто сбрасываем стили темной темы
        app.setStyleSheet("")