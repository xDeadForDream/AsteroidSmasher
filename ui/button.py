import math
import arcade


class Button:
    """Класс для красивых кнопок"""
    def __init__(self, x, y, width, height, text, color, hover_color, 
                 text_color=arcade.color.WHITE, font_size=24):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.is_hovered = False
        self.click_animation = 0
        self.pulse = 0

    def draw(self):
        self.pulse = (self.pulse + 0.1) % (math.pi * 2)
        pulse_offset = math.sin(self.pulse) * 3

        if self.is_hovered:
            color = self.hover_color
            scale = 1.05
        else:
            color = self.color
            scale = 1.0

        if self.click_animation > 0:
            self.click_animation -= 1
            scale = 0.95

        width = self.width * scale + pulse_offset
        height = self.height * scale + pulse_offset

        # Тень
        arcade.draw_lbwh_rectangle_filled(
            self.x - width/2 + 5,
            self.y - height/2 - 5,
            width, height,
            (0, 0, 0, 100)
        )

        # Градиент кнопки
        for i in range(3):
            alpha = 100 - i * 30
            arcade.draw_lbwh_rectangle_filled(
                self.x - width/2 + i,
                self.y - height/2 + i,
                width - i*2, height - i*2,
                (*color, alpha) if isinstance(color, tuple) and len(color) == 3 else color
            )

        # Рамка
        arcade.draw_lbwh_rectangle_outline(
            self.x - width/2,
            self.y - height/2,
            width, height,
            arcade.color.WHITE, 2
        )

        # Текст
        arcade.draw_text(
            self.text,
            self.x, self.y,
            self.text_color,
            self.font_size,
            anchor_x="center",
            anchor_y="center",
            bold=True,
            font_name=("Arial Rounded MT Bold", "Arial", "Helvetica")
        )

    def check_hover(self, mouse_x, mouse_y):
        self.is_hovered = (
            self.x - self.width/2 < mouse_x < self.x + self.width/2 and
            self.y - self.height/2 < mouse_y < self.y + self.height/2
        )
        return self.is_hovered

    def click(self):
        self.click_animation = 10
        return True