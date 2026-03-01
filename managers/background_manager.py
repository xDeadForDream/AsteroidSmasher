import random
import math
import arcade
import json
import os
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BACKGROUND_SPACE, BACKGROUND_NEBULA, BACKGROUND_STARS, BACKGROUND_GALAXY,
    BACKGROUND_COUNT, BACKGROUND_NAMES, BACKGROUND_COLORS
)


class BackgroundManager:
    """Класс для управления фонами"""
    def __init__(self):
        self.current_background = BACKGROUND_SPACE
        self.stars_far = []
        self.stars_near = []
        self.nebula_particles = []
        self.galaxy_particles = []
        self.load_settings()
        self.init_background()

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.current_background = settings.get('background', BACKGROUND_SPACE)
        except:
            pass

    def save_settings(self):
        try:
            settings = {}
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
            settings['background'] = self.current_background
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except:
            pass

    def init_background(self):
        self.stars_far = []
        for _ in range(150):
            self.stars_far.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.uniform(0.5, 1.5),
                'brightness': random.uniform(100, 200),
                'speed': 0.1,
                'twinkle_speed': random.uniform(0.5, 2.0)
            })

        self.stars_near = []
        for _ in range(75):
            self.stars_near.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.uniform(1.5, 2.5),
                'brightness': random.uniform(150, 255),
                'speed': 0.3,
                'twinkle_speed': random.uniform(1.0, 3.0)
            })

        self.nebula_particles = []
        for _ in range(50):
            self.nebula_particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.uniform(50, 200),
                'alpha': random.uniform(10, 40),
                'color': random.choice([
                    (100, 0, 150),
                    (150, 0, 100),
                    (80, 0, 200),
                    (120, 0, 180)
                ]),
                'drift_x': random.uniform(-0.2, 0.2),
                'drift_y': random.uniform(-0.2, 0.2)
            })

        self.galaxy_particles = []
        for _ in range(150):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, WINDOW_WIDTH * 0.7)
            self.galaxy_particles.append({
                'angle': angle,
                'distance': distance,
                'size': random.uniform(1, 4),
                'brightness': random.uniform(100, 255),
                'color': random.choice([
                    (255, 200, 100),
                    (200, 150, 255),
                    (150, 200, 255),
                    (255, 150, 150)
                ])
            })

    def draw(self, delta_time, ship_x=0, ship_y=0):
        color = BACKGROUND_COLORS[self.current_background]
        arcade.draw_lbwh_rectangle_filled(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, color)

        if self.current_background == BACKGROUND_SPACE:
            self.draw_space(delta_time, ship_x, ship_y)
        elif self.current_background == BACKGROUND_NEBULA:
            self.draw_nebula(delta_time, ship_x, ship_y)
        elif self.current_background == BACKGROUND_STARS:
            self.draw_stars(delta_time, ship_x, ship_y)
        elif self.current_background == BACKGROUND_GALAXY:
            self.draw_galaxy(delta_time, ship_x, ship_y)

    def draw_space(self, delta_time, ship_x, ship_y):
        for star in self.stars_far + self.stars_near:
            twinkle = math.sin(delta_time * star['twinkle_speed'] * 3) * 0.3 + 0.7
            brightness = int(star['brightness'] * twinkle)
            arcade.draw_point(
                star['x'], star['y'],
                (brightness, brightness, brightness),
                star['size']
            )

    def draw_nebula(self, delta_time, ship_x, ship_y):
        self.draw_space(delta_time, ship_x, ship_y)
        for particle in self.nebula_particles:
            particle['x'] += particle['drift_x']
            particle['y'] += particle['drift_y']

            if particle['x'] < -particle['size']:
                particle['x'] = WINDOW_WIDTH + particle['size']
            if particle['x'] > WINDOW_WIDTH + particle['size']:
                particle['x'] = -particle['size']
            if particle['y'] < -particle['size']:
                particle['y'] = WINDOW_HEIGHT + particle['size']
            if particle['y'] > WINDOW_HEIGHT + particle['size']:
                particle['y'] = -particle['size']

            pulse = math.sin(delta_time * 2 + particle['x'] * 0.01) * 0.2 + 0.8
            alpha = int(particle['alpha'] * pulse)
            color = particle['color']
            arcade.draw_circle_filled(
                particle['x'], particle['y'],
                particle['size'],
                (color[0], color[1], color[2], alpha)
            )

    def draw_stars(self, delta_time, ship_x, ship_y):
        for star in self.stars_far:
            star['x'] -= ship_x * star['speed']
            star['y'] -= ship_y * star['speed']

            if star['x'] < 0:
                star['x'] = WINDOW_WIDTH
            if star['x'] > WINDOW_WIDTH:
                star['x'] = 0
            if star['y'] < 0:
                star['y'] = WINDOW_HEIGHT
            if star['y'] > WINDOW_HEIGHT:
                star['y'] = 0

            twinkle = math.sin(delta_time * star['twinkle_speed']) * 0.2 + 0.8
            brightness = int(star['brightness'] * twinkle)
            arcade.draw_point(
                star['x'], star['y'],
                (brightness, brightness, brightness),
                star['size']
            )

        for star in self.stars_near:
            star['x'] -= ship_x * star['speed']
            star['y'] -= ship_y * star['speed']

            if star['x'] < 0:
                star['x'] = WINDOW_WIDTH
            if star['x'] > WINDOW_WIDTH:
                star['x'] = 0
            if star['y'] < 0:
                star['y'] = WINDOW_HEIGHT
            if star['y'] > WINDOW_HEIGHT:
                star['y'] = 0

            twinkle = math.sin(delta_time * star['twinkle_speed'] * 2) * 0.3 + 0.7
            brightness = int(star['brightness'] * twinkle)
            arcade.draw_point(
                star['x'], star['y'],
                (brightness, brightness, brightness),
                star['size']
            )

    def draw_galaxy(self, delta_time, ship_x, ship_y):
        arcade.draw_lbwh_rectangle_filled(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (5, 5, 15))
        center_x = WINDOW_WIDTH / 2
        center_y = WINDOW_HEIGHT / 2

        for i in range(300):
            angle = delta_time * 0.1 + i * 0.1
            distance = i * 2
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance

            if 0 < x < WINDOW_WIDTH and 0 < y < WINDOW_HEIGHT:
                brightness = int(100 + 55 * math.sin(angle * 5))
                size = 1 + (i % 3) * 0.5
                arcade.draw_point(
                    x, y,
                    (brightness, brightness, brightness + 50),
                    size
                )

        for particle in self.galaxy_particles:
            angle = particle['angle'] + delta_time * 0.05
            distance = particle['distance']
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance

            if 0 < x < WINDOW_WIDTH and 0 < y < WINDOW_HEIGHT:
                brightness = int(particle['brightness'] * (0.8 + 0.2 * math.sin(delta_time * 3 + angle)))
                color = particle['color']
                arcade.draw_point(
                    x, y,
                    (color[0], color[1], color[2]),
                    particle['size']
                )

    def next_background(self):
        self.current_background = (self.current_background + 1) % BACKGROUND_COUNT
        self.save_settings()
        return self.current_background

    def prev_background(self):
        self.current_background = (self.current_background - 1) % BACKGROUND_COUNT
        self.save_settings()
        return self.current_background