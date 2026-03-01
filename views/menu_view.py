import random
import math
import arcade
import time
import json
import os
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    DIFFICULTY_NORMAL, DIFFICULTY_EASY, DIFFICULTY_NAMES, DIFFICULTY_COLORS,
    BACKGROUND_NAMES
)
from ui.button import Button
from ui.nickname_input import NicknameInput
from managers.background_manager import BackgroundManager


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_manager = BackgroundManager()
        self.nickname = ""
        self.load_nickname()
        self.difficulty = DIFFICULTY_NORMAL
        self.load_difficulty()
        self.buttons = []
        self.init_buttons()
        self.nickname_input = NicknameInput(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 150,
            400, 60
        )
        self.nickname_input.text = self.nickname
        self.start_time = time.time()
        self.floating_elements = self.create_floating_elements()

    def load_nickname(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.nickname = settings.get('nickname', '')
        except:
            pass

    def save_nickname(self):
        try:
            settings = {}
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
            settings['nickname'] = self.nickname_input.text
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except:
            pass

    def load_difficulty(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.difficulty = settings.get('difficulty', DIFFICULTY_NORMAL)
        except:
            pass

    def save_difficulty(self):
        try:
            settings = {}
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
            settings['difficulty'] = self.difficulty
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except:
            pass

    def init_buttons(self):
        self.start_button = Button(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 100,
            400, 90,
            "🚀 СТАРТ",
            (50, 150, 255),
            (100, 200, 255),
            font_size=40
        )
        self.buttons.append(self.start_button)

        self.bg_button = Button(
            WINDOW_WIDTH / 2 - 200,
            WINDOW_HEIGHT / 2 - 230,
            250, 60,
            f"{BACKGROUND_NAMES[self.background_manager.current_background]}",
            (80, 80, 150),
            (130, 130, 200),
            font_size=20
        )
        self.buttons.append(self.bg_button)

        self.diff_button = Button(
            WINDOW_WIDTH / 2 + 200,
            WINDOW_HEIGHT / 2 - 230,
            250, 60,
            f"{DIFFICULTY_NAMES[self.difficulty]}",
            DIFFICULTY_COLORS[self.difficulty],
            (255, 255, 100) if self.difficulty == DIFFICULTY_NORMAL else
            (200, 255, 200) if self.difficulty == DIFFICULTY_EASY else (255, 200, 200),
            font_size=20
        )
        self.buttons.append(self.diff_button)

        self.quit_button = Button(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 330,
            200, 50,
            "🚪 ВЫХОД",
            (150, 50, 50),
            (200, 100, 100),
            font_size=24
        )
        self.buttons.append(self.quit_button)

    def create_floating_elements(self):
        elements = []
        for _ in range(20):
            elements.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.uniform(2, 6),
                'speed': random.uniform(0.5, 2),
                'angle': random.uniform(0, math.pi * 2),
                'type': random.choice(['asteroid', 'star', 'ship'])
            })
        return elements

    def on_draw(self):
        self.clear()
        current_time = time.time() - self.start_time
        self.background_manager.draw(current_time)

        # Плавающие элементы
        for element in self.floating_elements:
            if element['type'] == 'star':
                brightness = 100 + 55 * math.sin(current_time * 2 + element['x'])
                arcade.draw_point(
                    element['x'], element['y'],
                    (int(brightness), int(brightness), int(brightness)),
                    element['size']
                )

        # Затемнение
        arcade.draw_lbwh_rectangle_filled(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (0, 0, 0, 150))

        # Заголовок
        title_y = WINDOW_HEIGHT / 2 + 300
        title_pulse = math.sin(current_time * 3) * 10

        # Тень заголовка
        arcade.draw_text(
            "ASTEROID SMASHER",
            WINDOW_WIDTH / 2 + 5,
            title_y - 5,
            (0, 0, 0, 100),
            72,
            anchor_x="center",
            anchor_y="center",
            bold=True,
            font_name=("Arial Rounded MT Bold", "Arial", "Helvetica")
        )

        # Основной заголовок
        arcade.draw_text(
            "ASTEROID SMASHER",
            WINDOW_WIDTH / 2,
            title_y + title_pulse,
            arcade.color.WHITE,
            72,
            anchor_x="center",
            anchor_y="center",
            bold=True,
            font_name=("Arial Rounded MT Bold", "Arial", "Helvetica")
        )

        # Подзаголовок
        arcade.draw_text(
            "© 2026 КОСМИЧЕСКИЙ АРКАДА",
            WINDOW_WIDTH / 2,
            title_y - 50,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center"
        )

        # Подпись никнейма
        arcade.draw_text(
            "👤 НИКНЕЙМ ПИЛОТА",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 220,
            arcade.color.CYAN,
            20,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Поле ввода
        self.nickname_input.draw()

        # Кнопки
        for button in self.buttons:
            button.draw()

        # Управление
        arcade.draw_text(
            "УПРАВЛЕНИЕ: ← → ПОВОРОТ | ↑ ↓ ТЯГА | ПРОБЕЛ ОГОНЬ | C - СУПЕР-АТАКА",
            WINDOW_WIDTH / 2,
            50,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            "B/V - СМЕНА ФОНА | D - СЛОЖНОСТЬ | ESC - МЕНЮ",
            WINDOW_WIDTH / 2,
            20,
            arcade.color.GRAY,
            14,
            anchor_x="center",
            anchor_y="center"
        )

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        from views.game_view import GameView
        # Проверка клика по полю ввода
        if (self.nickname_input.x - self.nickname_input.width/2 < x <
            self.nickname_input.x + self.nickname_input.width/2 and
            self.nickname_input.y - self.nickname_input.height/2 < y <
            self.nickname_input.y + self.nickname_input.height/2):
            self.nickname_input.is_active = True
        else:
            self.nickname_input.is_active = False

        # Проверка кнопок
        for btn in self.buttons:
            if btn.check_hover(x, y):
                btn.click()

                if btn == self.start_button:
                    if self.nickname_input.text.strip() == "":
                        self.nickname_input.set_error("ВВЕДИ НИКНЕЙМ!")
                    else:
                        self.save_nickname()
                        game = GameView()
                        game.setup(self.background_manager, self.difficulty, self.nickname_input.text)
                        self.window.show_view(game)

                elif btn == self.bg_button:
                    index = self.background_manager.next_background()
                    btn.text = f"{BACKGROUND_NAMES[index]}"

                elif btn == self.diff_button:
                    self.difficulty = (self.difficulty + 1) % 3
                    btn.text = f"{DIFFICULTY_NAMES[self.difficulty]}"
                    btn.color = DIFFICULTY_COLORS[self.difficulty]

                    if self.difficulty == DIFFICULTY_EASY:
                        btn.hover_color = (200, 255, 200)
                    elif self.difficulty == DIFFICULTY_NORMAL:
                        btn.hover_color = (255, 255, 100)
                    else:
                        btn.hover_color = (255, 200, 200)
                    self.save_difficulty()

                elif btn == self.quit_button:
                    self.window.close()

    def on_key_press(self, symbol, modifiers):
        self.nickname_input.handle_key(symbol, modifiers)

        if symbol == arcade.key.ESCAPE:
            self.window.close()
        elif symbol == arcade.key.B and not self.nickname_input.is_active:
            index = self.background_manager.next_background()
            self.bg_button.text = f"{BACKGROUND_NAMES[index]}"
        elif symbol == arcade.key.V and not self.nickname_input.is_active:
            index = self.background_manager.prev_background()
            self.bg_button.text = f"{BACKGROUND_NAMES[index]}"
        elif symbol == arcade.key.D and not self.nickname_input.is_active:
            self.difficulty = (self.difficulty + 1) % 3
            self.diff_button.text = f"{DIFFICULTY_NAMES[self.difficulty]}"
            self.diff_button.color = DIFFICULTY_COLORS[self.difficulty]
            self.save_difficulty()

    def on_update(self, delta_time):
        self.nickname_input.update()

        # Анимация плавающих элементов
        for element in self.floating_elements:
            element['y'] += math.sin(element['angle']) * element['speed'] * 0.1
            element['angle'] += 0.01

            if element['y'] > WINDOW_HEIGHT + 50:
                element['y'] = -50
            if element['y'] < -50:
                element['y'] = WINDOW_HEIGHT + 50