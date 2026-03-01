import math
import arcade
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, MAX_SPEED, DRAG, SCALE


class TurningSprite(arcade.Sprite):
    def update(self, delta_time=1/60):
        super().update(delta_time)
        if self.change_x != 0 or self.change_y != 0:
            self.angle = -math.degrees(math.atan2(self.change_y, self.change_x))


class ShipSprite(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale=scale)
        self.thrust = 0
        self.speed = 0
        self.max_speed = MAX_SPEED
        self.drag = DRAG
        self.respawning = 0
        self.respawn()

    def respawn(self):
        self.respawning = 1
        self.alpha = 0
        self.center_x = WINDOW_WIDTH / 2
        self.center_y = WINDOW_HEIGHT / 2
        self.angle = 0
        self.speed = 0
        self.change_x = 0
        self.change_y = 0

    def update(self, delta_time: float = 1/60):
        if self.respawning:
            self.respawning += 1
            self.alpha = min(self.respawning * 8, 255)
            if self.respawning > 30:
                self.respawning = 0
                self.alpha = 255

        if not self.respawning and self.thrust != 0:
            self.speed += self.thrust
            if abs(self.speed) > self.max_speed:
                self.speed = self.max_speed if self.speed > 0 else -self.max_speed

        if abs(self.speed) > 0:
            if self.speed > 0:
                self.speed = max(0, self.speed - self.drag)
            else:
                self.speed = min(0, self.speed + self.drag)

        self.change_x = math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.right < 0:
            self.left = WINDOW_WIDTH
        elif self.left > WINDOW_WIDTH:
            self.right = 0
        if self.bottom < 0:
            self.top = WINDOW_HEIGHT
        elif self.top > WINDOW_HEIGHT:
            self.bottom = 0