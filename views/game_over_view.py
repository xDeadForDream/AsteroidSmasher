import math
import arcade
import time
import json
import os
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, DIFFICULTY_NAMES, DIFFICULTY_COLORS
from ui.button import Button


class GameOverView(arcade.View):
    def __init__(self, score, background_manager, difficulty, nickname, max_combo=0, wave=1):
        super().__init__()
        self.score = score
        self.nickname = nickname
        self.background_manager = background_manager
        self.difficulty = difficulty
        self.max_combo = max_combo
        self.wave = wave
        self.start_time = time.time()
        self.buttons = []
        self.init_buttons()
        self.highscores = self.load_highscores()
        self.save_score()

    def init_buttons(self):
        self.restart_button = Button(
            WINDOW_WIDTH / 2 - 250,
            WINDOW_HEIGHT / 2 - 200,
            350, 80,
            "🔄 ИГРАТЬ СНОВА",
            (50, 150, 50),
            (100, 200, 100),
            font_size=32
        )
        self.buttons.append(self.restart_button)

        self.menu_button = Button(
            WINDOW_WIDTH / 2 + 250,
            WINDOW_HEIGHT / 2 - 200,
            350, 80,
            "🏠 ГЛАВНОЕ МЕНЮ",
            (150, 150, 50),
            (200, 200, 100),
            font_size=32
        )
        self.buttons.append(self.menu_button)

    def load_highscores(self):
        try:
            if os.path.exists('highscores.json'):
                with open('highscores.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_score(self):
        try:
            highscores = self.load_highscores()
            highscores.append({
                'nickname': self.nickname,
                'score': self.score,
                'combo': self.max_combo,
                'difficulty': DIFFICULTY_NAMES[self.difficulty],
                'wave': self.wave,
                'date': time.strftime('%d.%m.%Y')
            })
            highscores = sorted(highscores, key=lambda x: x['score'], reverse=True)[:10]
            with open('highscores.json', 'w') as f:
                json.dump(highscores, f)
        except:
            pass

    def on_draw(self):
        self.clear()
        current_time = time.time() - self.start_time

        self.background_manager.draw(current_time)
        arcade.draw_lbwh_rectangle_filled(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (0, 0, 0, 200))

        # GAME OVER с пульсацией
        game_over_pulse = math.sin(current_time * 5) * 20 + 235
        arcade.draw_text(
            "GAME OVER",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 200,
            (int(game_over_pulse), 50, 50),
            72,
            anchor_x="center",
            anchor_y="center",
            bold=True,
            font_name=("Arial Rounded MT Bold", "Arial", "Helvetica")
        )

        # Статистика
        arcade.draw_text(
            f"👤 ПИЛОТ: {self.nickname}",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 100,
            arcade.color.WHITE,
            32,
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            f"💯 СЧЕТ: {self.score}",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 40,
            arcade.color.YELLOW,
            36,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            f"🔥 МАКС. КОМБО: {self.max_combo}x",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 20,
            arcade.color.ORANGE,
            28,
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            f"🌊 ДОСТИГНУТ УРОВЕНЬ: {self.wave}",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 80,
            arcade.color.CYAN,
            28,
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            f"⚡ СЛОЖНОСТЬ: {DIFFICULTY_NAMES[self.difficulty]}",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 140,
            DIFFICULTY_COLORS[self.difficulty],
            24,
            anchor_x="center",
            anchor_y="center"
        )

        # Таблица рекордов
        arcade.draw_text(
            "🏆 ТАБЛИЦА РЕКОРДОВ",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 300,
            arcade.color.GOLD,
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        y = WINDOW_HEIGHT / 2 - 350
        for i, record in enumerate(self.load_highscores()[:5]):
            color = (
                arcade.color.GOLD if i == 0 
                else arcade.color.SILVER if i == 1 
                else arcade.color.BRONZE if i == 2 
                else arcade.color.WHITE
            )
            arcade.draw_text(
                f"{i+1}. {record['nickname']} - {record['score']} pts | {record['combo']}x | Ур.{record['wave']} | {record['difficulty']}",
                WINDOW_WIDTH / 2,
                y,
                color,
                18,
                anchor_x="center",
                anchor_y="center"
            )
            y -= 30

        # Кнопки
        for button in self.buttons:
            button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        from views.menu_view import MenuView
        from views.game_view import GameView
        for btn in self.buttons:
            if btn.check_hover(x, y):
                btn.click()

                if btn == self.restart_button:
                    game = GameView()
                    game.setup(self.background_manager, self.difficulty, self.nickname)
                    self.window.show_view(game)
                elif btn == self.menu_button:
                    menu = MenuView()
                    self.window.show_view(menu)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            menu = MenuView()
            self.window.show_view(menu)
        elif symbol in (arcade.key.ENTER, arcade.key.SPACE, arcade.key.R):
            game = GameView()
            game.setup(self.background_manager, self.difficulty, self.nickname)
            self.window.show_view(game)