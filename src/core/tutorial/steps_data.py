"""
Данные шагов обучения для бота Sea of Conquest.
Файл содержит только определения шагов, без логики выполнения.
"""

# Словарь с данными сезонов и соответствующих им диапазонов серверов
SEASON_SERVER_RANGES = {
    "Сезон S1": (577, 600),
    "Сезон S2": (541, 576),
    "Сезон S3": (505, 540),
    "Сезон S4": (481, 504),
    "Сезон S5": (433, 480),
    "Сезон X1": (409, 432),
    "Сезон X2": (266, 407),
    "Сезон X3": (1, 264),
}

# Видимые сезоны на экране без скролла
VISIBLE_SEASONS = ["Сезон S1", "Сезон S2", "Сезон S3", "Сезон S4", "Сезон S5", "Сезон X1"]

# Скрытые сезоны, требующие скролла
HIDDEN_SEASONS = ["Сезон X2", "Сезон X3"]

# Список шагов обучения, представленных в виде словарей для инициализации TutorialStep
TUTORIAL_STEPS_DATA = [
    # Шаг 1: Клик по иконке профиля
    {
        "step_id": 1,
        "description": "Клик по иконке профиля",
        "action_type": "click_image",
        "image_name": "open_profile"
    },

    # Шаг 2: Клик по иконке настроек
    {
        "step_id": 2,
        "description": "Клик по иконке настроек",
        "action_type": "click",
        "x": 1073, "y": 35
    },

    # Шаг 3: Клик по иконке персонажей
    {
        "step_id": 3,
        "description": "Клик по иконке персонажей",
        "action_type": "click",
        "x": 638, "y": 319
    },

    # Шаг 4: Клик по иконке добавления персонажей
    {
        "step_id": 4,
        "description": "Клик по иконке добавления персонажей",
        "action_type": "click",
        "x": 270, "y": 184
    },

    # Шаг 5: Парсинг сезона и клик по нужному
    {
        "step_id": 5,
        "description": "Выбор сезона",
        "action_type": "select_season",
    },

    # Шаг 6: Парсинг и клик по нужному серверу
    {
        "step_id": 6,
        "description": "Выбор сервера",
        "action_type": "select_server",
    },

    # Шаг 7: Клик по кнопке подтвердить
    {
        "step_id": 7,
        "description": "Подтверждение выбора аккаунта",
        "action_type": "click_image",
        "image_name": "confirm_new_acc"
    },

    # Шаг 8: Ожидание загрузки
    {
        "step_id": 8,
        "description": "Ожидание загрузки",
        "action_type": "wait",
        "seconds": 10
    },

    # Шаг 9: Поиск и клик по картинке skip.png
    {
        "step_id": 9,
        "description": "Поиск и клик по кнопке пропуска",
        "action_type": "find_and_click_or_repeat",
        "image_name": "skip",
        "max_attempts": 10,
        "wait_between_attempts": 4,
        "click_random_if_not_found": True,
        "random_center_x": 640,
        "random_center_y": 360,
        "random_radius": 150
    },

    # Шаг 10: Поиск и клик по skip.png или shoot.png
    {
        "step_id": 10,
        "description": "Поиск и клик по skip или shoot",
        "action_type": "find_and_click_multiple",
        "images": ["skip", "shoot"],
        "priority_image": "shoot",
        "next_step_on_priority": 11
    },

    # Шаг 11: Ожидание и клик по skip.png
    {
        "step_id": 11,
        "description": "Ожидание и клик по skip",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 12: Ожидание появления Hell_Genry.png
    {
        "step_id": 12,
        "description": "Ожидание появления Hell_Genry",
        "action_type": "wait_for_image",
        "image_name": "Hell_Genry",
        "timeout": 60,
        "check_interval": 2
    },

    # Шаг 13: Клик по lite_apks.png
    {
        "step_id": 13,
        "description": "Клик по lite_apks",
        "action_type": "click_image",
        "image_name": "lite_apks"
    },

    # Шаг 14: Сложный свайп
    {
        "step_id": 14,
        "description": "Сложный свайп",
        "action_type": "complex_swipe",
        "points": [(154, 351), (288, 355), (507, 353), (627, 351)],
        "duration_ms": 1500
    },

    # Шаг 15: Клик по close_menu.png
    {
        "step_id": 15,
        "description": "Закрытие меню",
        "action_type": "click_image",
        "image_name": "close_menu"
    },

    # Шаг 16: Клик по skip.png
    {
        "step_id": 16,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 17: Клик по ship.png
    {
        "step_id": 17,
        "description": "Клик по кораблю",
        "action_type": "click_image",
        "image_name": "ship"
    },

    # Шаг 18: Клик по skip.png
    {
        "step_id": 18,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 19: Ожидание 5 секунд
    {
        "step_id": 19,
        "description": "Ожидание 5 секунд",
        "action_type": "wait",
        "seconds": 5
    },

    # Шаг 20: Клик по координатам (637, 368)
    {
        "step_id": 20,
        "description": "Клик по координатам (637, 368)",
        "action_type": "click",
        "x": 637, "y": 368
    },

    # Шаг 21: Клик по координатам (637, 368)
    {
        "step_id": 21,
        "description": "Клик по координатам (637, 368)",
        "action_type": "click",
        "x": 637, "y": 368
    },

    # Шаг 22: Клик по координатам (637, 368)
    {
        "step_id": 22,
        "description": "Клик по координатам (637, 368)",
        "action_type": "click",
        "x": 637, "y": 368
    },

    # Шаг 23: Клик по картинке skip.png
    {
        "step_id": 23,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 24: Клик по координатам (342, 387)
    {
        "step_id": 24,
        "description": "Клик по координатам (342, 387)",
        "action_type": "click",
        "x": 342, "y": 387
    },

    # Шаг 25: Клик по координатам (79, 294)
    {
        "step_id": 25,
        "description": "Клик по координатам (79, 294)",
        "action_type": "click",
        "x": 79, "y": 294
    },

    # Шаг 26: Клик по картинке skip.png
    {
        "step_id": 26,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 27: Клик по координатам (739, 137)
    {
        "step_id": 27,
        "description": "Клик по координатам (739, 137)",
        "action_type": "click",
        "x": 739, "y": 137
    },

    # Шаг 28: Клик по картинке skip.png
    {
        "step_id": 28,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 29: Клик по координатам (146, 286)
    {
        "step_id": 29,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 30: Клик по картинке skip.png
    {
        "step_id": 30,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 31: Клик по координатам (146, 286)
    {
        "step_id": 31,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 32: Клик по картинке skip.png
    {
        "step_id": 32,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 33: Клик по картинке skip.png
    {
        "step_id": 33,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 34: Клик по координатам (146, 286)
    {
        "step_id": 34,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 35: Клик по картинке skip.png
    {
        "step_id": 35,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 36: Клик по картинке navigator.png
    {
        "step_id": 36,
        "description": "Клик по навигатору",
        "action_type": "click_image",
        "image_name": "navigator"
    },

    # Шаг 37: Клик по координатам (699, 269)
    {
        "step_id": 37,
        "description": "Клик по координатам (699, 269)",
        "action_type": "click",
        "x": 699, "y": 269
    },

    # Шаг 38: Клик по картинке skip.png
    {
        "step_id": 38,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 39: Клик по координатам (141, 30)
    {
        "step_id": 39,
        "description": "Клик по координатам (141, 30)",
        "action_type": "click",
        "x": 141, "y": 30
    },

    # Шаг 40: Клик по картинке skip.png
    {
        "step_id": 40,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 41: Клик по координатам (146, 286)
    {
        "step_id": 41,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 42: Клик по картинке skip.png
    {
        "step_id": 42,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 43: Задержка перед кликом 2 сек, клик по координатам (146, 286)
    {
        "step_id": 43,
        "description": "Задержка 2 сек и клик по координатам (146, 286)",
        "action_type": "delayed_click",
        "x": 146, "y": 286,
        "delay_seconds": 2
    },

    # Шаг 44: Клик по картинке skip.png
    {
        "step_id": 44,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 45: Клик по координатам (228, 341)
    {
        "step_id": 45,
        "description": "Клик по координатам (228, 341)",
        "action_type": "click",
        "x": 228, "y": 341
    },

    # Шаг 46: Клик по картинке skip.png
    {
        "step_id": 46,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 47: Клик по координатам (228, 341)
    {
        "step_id": 47,
        "description": "Клик по координатам (228, 341)",
        "action_type": "click",
        "x": 228, "y": 341
    },

    # Шаг 48: Клик по картинке skip.png
    {
        "step_id": 48,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 49: Клик по картинке hero_face.png
    {
        "step_id": 49,
        "description": "Клик по изображению героя",
        "action_type": "click_image",
        "image_name": "hero_face"
    },

    # Шаг 50: Клик по картинке start_battle.png
    {
        "step_id": 50,
        "description": "Клик по кнопке начала битвы",
        "action_type": "click_image",
        "image_name": "start_battle"
    },

    # Шаг 51: Клик по координатам (642, 324) каждые 1,5 сек пока не найдена картинка start_battle.png
    {
        "step_id": 51,
        "description": "Клик (642, 324) до появления кнопки начала битвы",
        "action_type": "repeat_click_until_image",
        "x": 642, "y": 324,
        "interval_seconds": 1.5,
        "target_image": "start_battle",
        "click_on_image": True
    },

    # Шаг 52: Клик по координатам (642, 324) каждые 1,5 (не более 7 раз) пока не найдена картинка skip.png
    {
        "step_id": 52,
        "description": "Клик (642, 324) до появления кнопки пропуска",
        "action_type": "repeat_click_until_image",
        "x": 642, "y": 324,
        "interval_seconds": 1.5,
        "max_attempts": 7,
        "target_image": "skip",
        "click_on_image": True
    },

    # Шаг 53: Клик по координатам (146, 286)
    {
        "step_id": 53,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 54: Клик по картинке skip.png
    {
        "step_id": 54,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 55: Клик по координатам (146, 286)
    {
        "step_id": 55,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 56: Клик по картинке skip.png
    {
        "step_id": 56,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 57: Клик по координатам (656, 405)
    {
        "step_id": 57,
        "description": "Клик по координатам (656, 405)",
        "action_type": "click",
        "x": 656, "y": 405
    },

    # Шаг 58: Клик по картинке skip.png
    {
        "step_id": 58,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 59: Клик по картинке skip.png
    {
        "step_id": 59,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 60: Клик по картинке skip.png
    {
        "step_id": 60,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 61: Клик по картинке skip.png (в ТЗ это шаг 70)
    {
        "step_id": 61,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 62: Клик по картинке skip.png (в ТЗ это шаг 71)
    {
        "step_id": 62,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 63: Клик по картинке skip.png (в ТЗ это шаг 72)
    {
        "step_id": 63,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 64: Клик по координатам (146, 286) (в ТЗ это шаг 73)
    {
        "step_id": 64,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 65: Клик по картинке skip.png (в ТЗ это шаг 74)
    {
        "step_id": 65,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 66: Клик по координатам (146, 286) (в ТЗ это шаг 75)
    {
        "step_id": 66,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 67: Клик по координатам (44, 483) (в ТЗ это шаг 76)
    {
        "step_id": 67,
        "description": "Клик по координатам (44, 483)",
        "action_type": "click",
        "x": 44, "y": 483
    },

    # Шаг 68: Клик по координатам (128, 226) (в ТЗ это шаг 77)
    {
        "step_id": 68,
        "description": "Клик по координатам (128, 226)",
        "action_type": "click",
        "x": 128, "y": 226
    },

    # Шаг 69: Клик по картинке upgrade_ship.png (в ТЗ это шаг 78)
    {
        "step_id": 69,
        "description": "Клик по кнопке улучшения корабля",
        "action_type": "click_image",
        "image_name": "upgrade_ship"
    },

    # Шаг 70: Клик по координатам (144, 24) (в ТЗ это шаг 79)
    {
        "step_id": 70,
        "description": "Клик по координатам (144, 24)",
        "action_type": "click",
        "x": 144, "y": 24
    },

    # Шаг 71: Клик по координатам (639, 598) (в ТЗ это шаг 80)
    {
        "step_id": 71,
        "description": "Клик по координатам (639, 598)",
        "action_type": "click",
        "x": 639, "y": 598
    },

    # Шаг 72: Клик по картинке skip.png (в ТЗ это шаг 90)
    {
        "step_id": 72,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 73: Клик по координатам (1075, 91) (в ТЗ это шаг 91)
    {
        "step_id": 73,
        "description": "Клик по координатам (1075, 91)",
        "action_type": "click",
        "x": 1075, "y": 91
    },

    # Шаг 74: Клик по координатам (146, 286) (в ТЗ это шаг 92)
    {
        "step_id": 74,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 75: Клик по координатам (41, 483) (в ТЗ это шаг 93)
    {
        "step_id": 75,
        "description": "Клик по координатам (41, 483)",
        "action_type": "click",
        "x": 41, "y": 483
    },

    # Шаг 76: Клик по координатам (975, 510) (в ТЗ это шаг 94)
    {
        "step_id": 76,
        "description": "Клик по координатам (975, 510)",
        "action_type": "click",
        "x": 975, "y": 510
    },

    # Шаг 77: Клик по координатам (746, 599) (в ТЗ это шаг 95)
    {
        "step_id": 77,
        "description": "Клик по координатам (746, 599)",
        "action_type": "click",
        "x": 746, "y": 599
    },

    # Шаг 78: Клик по координатам (639, 491) (в ТЗ это шаг 96)
    {
        "step_id": 78,
        "description": "Клик по координатам (639, 491)",
        "action_type": "click",
        "x": 639, "y": 491
    },

    # Шаг 79: Клик по координатам (146, 286) (в ТЗ это шаг 97)
    {
        "step_id": 79,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 80: Клик по координатам (146, 286) (в ТЗ это шаг 98)
    {
        "step_id": 80,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 81: Клик по координатам (41, 483) (в ТЗ это шаг 99)
    {
        "step_id": 81,
        "description": "Клик по координатам (41, 483)",
        "action_type": "click",
        "x": 41, "y": 483
    },

    # Шаг 82: Клик по координатам (692, 504) (в ТЗ это шаг 100)
    {
        "step_id": 82,
        "description": "Клик по координатам (692, 504)",
        "action_type": "click",
        "x": 692, "y": 504
    },

    # Шаг 83: Клик по координатам (691, 584) (в ТЗ это шаг 101)
    {
        "step_id": 83,
        "description": "Клик по координатам (691, 584)",
        "action_type": "click",
        "x": 691, "y": 584
    },

    # Шаг 84: Клик по координатам (665, 516) (в ТЗ это шаг 102)
    {
        "step_id": 84,
        "description": "Клик по координатам (665, 516)",
        "action_type": "click",
        "x": 665, "y": 516
    },

    # Шаг 85: Клик по координатам (146, 286) (в ТЗ это шаг 103)
    {
        "step_id": 85,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 86: Клик по координатам (146, 286) (в ТЗ это шаг 104)
    {
        "step_id": 86,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 87: Клик по картинке navigator.png (в ТЗ это шаг 105)
    {
        "step_id": 87,
        "description": "Клик по навигатору",
        "action_type": "click_image",
        "image_name": "navigator"
    },

    # Шаг 88: Клик по координатам (692, 282) (в ТЗ это шаг 106)
    {
        "step_id": 88,
        "description": "Клик по координатам (692, 282)",
        "action_type": "click",
        "x": 692, "y": 282
    },

    # Шаг 89: Клик по картинке skip.png (в ТЗ это шаг 107)
    {
        "step_id": 89,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 90: Клик по координатам (648, 210) (в ТЗ это шаг 108)
    {
        "step_id": 90,
        "description": "Клик по координатам (648, 210)",
        "action_type": "click",
        "x": 648, "y": 210
    },

    # Шаг 91: Клик по картинке skip.png (в ТЗ это шаг 109)
    {
        "step_id": 91,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 92: Клик по картинке skip.png (в ТЗ это шаг 110)
    {
        "step_id": 92,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 93: Клик по картинке skip.png (в ТЗ это шаг 111)
    {
        "step_id": 93,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 94: Клик по координатам (146, 286) (в ТЗ это шаг 112)
    {
        "step_id": 94,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 95: Клик по картинке skip.png (в ТЗ это шаг 113)
    {
        "step_id": 95,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 96: Клик по картинке skip.png (в ТЗ это шаг 114)
    {
        "step_id": 96,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 97: Клик по картинке skip.png (в ТЗ это шаг 115)
    {
        "step_id": 97,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 98: Клик по картинке skip.png (в ТЗ это шаг 116)
    {
        "step_id": 98,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 99: Ожидание 7 секунд и клик по координатам (967, 620) (в ТЗ это шаг 117)
    {
        "step_id": 99,
        "description": "Ожидание 7 секунд и клик по координатам (967, 620)",
        "action_type": "delayed_click",
        "x": 967, "y": 620,
        "delay_seconds": 7
    },

    # Шаг 100: Клик по картинке skip.png (в ТЗ это шаг 118)
    {
        "step_id": 100,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 101: Клик по координатам (146, 286) (в ТЗ это шаг 119)
    {
        "step_id": 101,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 102: Клик по картинке open_new_local_building.png (в ТЗ это шаг 120)
    {
        "step_id": 102,
        "description": "Клик по кнопке открытия нового локального строения",
        "action_type": "click_image",
        "image_name": "open_new_local_building"
    },

    # Шаг 103: Клик по картинке skip.png (в ТЗ это шаг 121)
    {
        "step_id": 103,
        "description": "Клик по кнопке пропуска",
        "action_type": "click_image",
        "image_name": "skip"
    },

    # Шаг 104: Клик по координатам (146, 286) (в ТЗ это шаг 122)
    {
        "step_id": 104,
        "description": "Клик по координатам (146, 286)",
        "action_type": "click",
        "x": 146, "y": 286
    },

    # Шаг 105: Закрытие игры (в ТЗ это шаг 123)
    {
        "step_id": 105,
        "description": "Закрытие игры",
        "action_type": "close_app",
        "package_name": "com.seaofconquest.global"
    },

    # Шаг 106: Запуск игры по новой (в ТЗ это шаг 124)
    {
        "step_id": 106,
        "description": "Запуск игры заново",
        "action_type": "start_app",
        "package_name": "com.seaofconquest.global",
        "activity_name": "com.kingsgroup.mo.KGUnityPlayerActivity"
    },

    # Шаг 107: Ожидание 10 секунд (в ТЗ указано второй раз как шаг 125)
    {
        "step_id": 107,
        "description": "Ожидание загрузки",
        "action_type": "wait",
        "seconds": 10
    },

    # Шаг 108: Нажатие ESC каждые 10 секунд для закрытия рекламы (в ТЗ это тоже шаг 125)
    {
        "step_id": 108,
        "description": "Закрытие рекламы и поиск иконки профиля",
        "action_type": "wait_for_image_with_esc",
        "image_name": "open_profile",
        "timeout": 120,
        "check_interval": 10,
        "esc_interval": 10
    }
]