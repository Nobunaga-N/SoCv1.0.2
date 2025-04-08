class TutorialStep:
    """Класс, представляющий один шаг в прохождении обучения."""

    def __init__(self, step_id: int, description: str, action_type: str, **kwargs):
        """
        Инициализация шага обучения.

        Args:
            step_id: Уникальный идентификатор шага
            description: Описание шага
            action_type: Тип действия ('click', 'click_image', 'swipe', 'wait', 'complex_swipe', и т.д.)
            **kwargs: Дополнительные параметры, зависящие от типа действия
        """
        self.step_id = step_id
        self.description = description
        self.action_type = action_type
        self.params = kwargs

    def __str__(self) -> str:
        """Строковое представление шага."""
        return f"Шаг {self.step_id}: {self.description} ({self.action_type})"

    def get_param(self, name, default=None):
        """
        Получает значение параметра с заданным именем.

        Args:
            name: Имя параметра
            default: Значение по умолчанию, если параметр не найден

        Returns:
            Значение параметра или значение по умолчанию
        """
        return self.params.get(name, default)

    def set_param(self, name, value):
        """
        Устанавливает значение параметра.

        Args:
            name: Имя параметра
            value: Новое значение параметра
        """
        self.params[name] = value