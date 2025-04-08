from PyQt6.QtWidgets import (QWidget, QPushButton, QLabel, QSpinBox, QComboBox,
                             QVBoxLayout, QHBoxLayout, QGroupBox, QTabWidget,
                             QTextEdit, QProgressBar, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QSizePolicy, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
import os


class UIFactory:
    """Фабрика для создания унифицированных компонентов UI."""

    @staticmethod
    def create_button(text, tooltip=None, icon=None, enabled=True):
        """Создает стилизованную кнопку."""
        button = QPushButton(text)

        if tooltip:
            button.setToolTip(tooltip)

        if icon:
            button.setIcon(QIcon(icon))

        button.setEnabled(enabled)
        button.setMinimumHeight(36)
        button.setFont(QFont("Segoe UI", 10))

        return button

    @staticmethod
    def create_label(text, bold=False, font_size=10, align=Qt.AlignmentFlag.AlignLeft):
        """Создает стилизованную метку."""
        label = QLabel(text)

        font = QFont("Segoe UI", font_size)
        if bold:
            font.setBold(True)

        label.setFont(font)
        label.setAlignment(align)

        return label

    @staticmethod
    def create_header_label(text, font_size=12):
        """Создает заголовок."""
        label = UIFactory.create_label(text, True, font_size, Qt.AlignmentFlag.AlignCenter)
        return label

    @staticmethod
    def create_spinbox(min_value, max_value, default_value, step=1, tooltip=None):
        """Создает спин-бокс с заданными параметрами."""
        spinbox = QSpinBox()
        spinbox.setMinimum(min_value)
        spinbox.setMaximum(max_value)
        spinbox.setValue(default_value)
        spinbox.setSingleStep(step)

        if tooltip:
            spinbox.setToolTip(tooltip)

        spinbox.setMinimumHeight(30)
        spinbox.setFont(QFont("Segoe UI", 10))

        return spinbox

    @staticmethod
    def create_combobox(items, default_index=0, tooltip=None):
        """Создает выпадающий список с заданными элементами."""
        combobox = QComboBox()

        for item in items:
            combobox.addItem(item)

        combobox.setCurrentIndex(default_index)

        if tooltip:
            combobox.setToolTip(tooltip)

        combobox.setMinimumHeight(30)
        combobox.setFont(QFont("Segoe UI", 10))

        return combobox

    @staticmethod
    def create_group(title, layout=None):
        """Создает группу с заданным заголовком и макетом."""
        group = QGroupBox(title)
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        if layout:
            group.setLayout(layout)

        return group

    @staticmethod
    def create_textedit(read_only=True, placeholder=None):
        """Создает текстовое поле для вывода информации."""
        textedit = QTextEdit()
        textedit.setReadOnly(read_only)

        if placeholder:
            textedit.setPlaceholderText(placeholder)

        textedit.setFont(QFont("Consolas", 9))

        return textedit

    @staticmethod
    def create_progressbar(min_value=0, max_value=100, initial_value=0):
        """Создает прогресс-бар с заданными параметрами."""
        progressbar = QProgressBar()
        progressbar.setMinimum(min_value)
        progressbar.setMaximum(max_value)
        progressbar.setValue(initial_value)
        progressbar.setTextVisible(True)
        progressbar.setMinimumHeight(20)

        return progressbar

    @staticmethod
    def create_table(headers, rows=0, stretch_last=True):
        """Создает таблицу с заданными заголовками."""
        table = QTableWidget(rows, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Устанавливаем растягивание последней колонки, если требуется
        if stretch_last:
            header = table.horizontalHeader()
            for i in range(len(headers) - 1):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(len(headers) - 1, QHeaderView.ResizeMode.Stretch)

        return table

    @staticmethod
    def create_horizontal_separator():
        """Создает горизонтальную разделительную линию."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    @staticmethod
    def create_vertical_separator():
        """Создает вертикальную разделительную линию."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    @staticmethod
    def create_scrollable_widget(widget):
        """Создает прокручиваемый виджет."""
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        return scroll