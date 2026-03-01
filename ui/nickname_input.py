import arcade


class NicknameInput:
    """Класс для ввода никнейма с исправленным Caps Lock"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = ""
        self.is_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = 15
        self.error_message = ""
        self.error_timer = 0

    def draw(self):
        if self.is_active:
            color = arcade.color.LIGHT_BLUE
        else:
            color = arcade.color.GRAY

        if self.is_active:
            for i in range(3):
                alpha = 50 - i * 15
                arcade.draw_lbwh_rectangle_filled(
                    self.x - self.width/2 - i,
                    self.y - self.height/2 - i,
                    self.width + i*2, self.height + i*2,
                    (100, 150, 255, alpha)
                )

        arcade.draw_lbwh_rectangle_filled(
            self.x - self.width/2,
            self.y - self.height/2,
            self.width, self.height,
            (30, 30, 50)
        )

        arcade.draw_lbwh_rectangle_outline(
            self.x - self.width/2,
            self.y - self.height/2,
            self.width, self.height,
            color, 3
        )

        display_text = self.text if self.text else "ВВЕДИ НИКНЕЙМ"
        text_color = arcade.color.WHITE if self.text else arcade.color.GRAY
        arcade.draw_text(
            display_text,
            self.x, self.y,
            text_color,
            24,
            anchor_x="center",
            anchor_y="center",
            font_name=("Arial Rounded MT Bold", "Arial", "Helvetica")
        )

        if self.is_active and self.cursor_visible:
            text_width = len(self.text) * 12
            cursor_x = self.x + text_width/2 + 5
            arcade.draw_line(
                cursor_x, self.y - 15,
                cursor_x, self.y + 15,
                arcade.color.WHITE, 2
            )

        if self.error_timer > 0:
            self.error_timer -= 1
            arcade.draw_text(
                self.error_message,
                self.x, self.y - 50,
                arcade.color.RED,
                18,
                anchor_x="center",
                anchor_y="center"
            )

    def update(self):
        self.cursor_timer = (self.cursor_timer + 1) % 30
        self.cursor_visible = self.cursor_timer < 15

    def handle_key(self, symbol, modifiers):
        if not self.is_active:
            return
        
        # Проверка на Backspace
        if symbol == arcade.key.BACKSPACE:
            self.text = self.text[:-1]
            return
            
        # Проверка на Enter
        if symbol == arcade.key.ENTER:
            self.is_active = False
            return

        if len(self.text) >= self.max_length:
            return

        # Обработка букв
        if 97 <= symbol <= 122: # a-z
            char = chr(symbol)
            # Логика Caps Lock и Shift:
            # Заглавная если: (Shift нажат И CapsLock выкл) ИЛИ (Shift не нажат И CapsLock вкл)
            is_shift = modifiers & arcade.key.MOD_SHIFT
            is_caps = modifiers & arcade.key.MOD_CAPSLOCK
            
            if (is_shift and not is_caps) or (not is_shift and is_caps):
                char = char.upper()
            # иначе оставляем строчной
            
            self.text += char
            return

        # Обработка цифр
        if 48 <= symbol <= 57:
            self.text += chr(symbol)
            return
            
        # Пробел
        if symbol == arcade.key.SPACE:
            self.text += " "
            return

    def set_error(self, message):
        self.error_message = message
        self.error_timer = 120