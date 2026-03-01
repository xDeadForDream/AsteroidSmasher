import arcade
from constants import WINDOW_WIDTH, WINDOW_HEIGHT


class AsteroidSprite(arcade.Sprite):
    def __init__(self, image_file_name, scale, type):
        super().__init__(image_file_name, scale=scale)
        self.type = type

    def update(self, delta_time: float = 1/60):
        super().update()
        if self.right < 0:
            self.left = WINDOW_WIDTH
        elif self.left > WINDOW_WIDTH:
            self.right = 0
        if self.top < 0:
            self.bottom = WINDOW_HEIGHT
        elif self.bottom > WINDOW_HEIGHT:
            self.top = 0