import random
import math
import arcade
import time
import json
import os
from typing import cast
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, SCALE,
    STARTING_ASTEROID_COUNT, MAX_SPEED, TURN_SPEED, THRUST_AMOUNT, DRAG,
    ASTEROID_TYPE_BIG, ASTEROID_TYPE_MEDIUM, ASTEROID_TYPE_SMALL,
    ASTEROID_DAMAGE,
    DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD,
    DIFFICULTY_NAMES, DIFFICULTY_COLORS,
    BACKGROUND_NAMES
)
from sprites.ship_sprite import TurningSprite, ShipSprite
from sprites.asteroid_sprite import AsteroidSprite
from managers.background_manager import BackgroundManager
from views.game_over_view import GameOverView


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.game_over = False
        self.background_manager = None
        self.difficulty = DIFFICULTY_NORMAL
        self.nickname = ""
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()
        self.score = 0
        self.player_sprite = None
        self.lives = 3.0
        self.max_lives = 5

        # Звуки
        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")

        # СУПЕР-АТАКА
        self.super_attack_ready = True
        self.super_attack_cooldown = 0
        self.super_attack_cooldown_max = 900
        self.super_attack_sound = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.super_attack_effect_timer = 0

        # ГОЛОСОВОЙ АНОНСЕР
        self.voice_perfect = arcade.load_sound(":resources:sounds/upgrade1.wav")
        self.voice_mega_kill = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.voice_game_over = arcade.load_sound(":resources:sounds/error4.wav")
        self.last_announcement = 0
        self.kill_streak = 0

        # СИСТЕМА УРОВНЕЙ
        self.current_wave = 1
        self.asteroids_destroyed_this_wave = 0
        self.asteroids_needed_for_next_wave = 5
        self.wave_transition_timer = 0
        self.wave_active = True

        self.text_score = None
        self.text_asteroid_count = None
        self.combo = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.combo_multiplier = 1

    def apply_difficulty_settings(self):
        global STARTING_ASTEROID_COUNT, MAX_SPEED, TURN_SPEED, THRUST_AMOUNT, DRAG
        if self.difficulty == DIFFICULTY_EASY:
            STARTING_ASTEROID_COUNT = 3
            MAX_SPEED = 7.0
            TURN_SPEED = 6
            THRUST_AMOUNT = 0.4
            DRAG = 0.015
            self.max_lives = 5
        elif self.difficulty == DIFFICULTY_NORMAL:
            STARTING_ASTEROID_COUNT = 5
            MAX_SPEED = 6.0
            TURN_SPEED = 5
            THRUST_AMOUNT = 0.35
            DRAG = 0.02
            self.max_lives = 3
        else:
            STARTING_ASTEROID_COUNT = 7
            MAX_SPEED = 5.0
            TURN_SPEED = 4
            THRUST_AMOUNT = 0.3
            DRAG = 0.025
            self.max_lives = 2

    def setup(self, background_manager=None, difficulty=DIFFICULTY_NORMAL, nickname="Пилот"):
        self.game_over = False
        self.difficulty = difficulty
        self.nickname = nickname
        self.apply_difficulty_settings()

        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        self.score = 0
        self.lives = self.max_lives
        self.super_attack_ready = True
        self.super_attack_cooldown = 0
        self.super_attack_effect_timer = 0
        self.kill_streak = 0
        self.last_announcement = 0

        # СИСТЕМА УРОВНЕЙ - СБРОС
        self.current_wave = 1
        self.asteroids_destroyed_this_wave = 0
        self.asteroids_needed_for_next_wave = 5
        self.wave_transition_timer = 0
        self.wave_active = True
        self.combo = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.combo_multiplier = 1

        if background_manager:
            self.background_manager = background_manager
        else:
            self.background_manager = BackgroundManager()

        self.player_sprite = ShipSprite(
            ":resources:images/space_shooter/playerShip1_orange.png",
            scale=SCALE,
        )
        self.player_sprite.angle = 0
        self.player_sprite.max_speed = MAX_SPEED
        self.player_sprite_list.append(self.player_sprite)
        self.update_life_display()

        # Создание астероидов
        image_list = (
            ":resources:images/space_shooter/meteorGrey_big1.png",
            ":resources:images/space_shooter/meteorGrey_big2.png",
            ":resources:images/space_shooter/meteorGrey_big3.png",
            ":resources:images/space_shooter/meteorGrey_big4.png",
        )

        for _ in range(STARTING_ASTEROID_COUNT):
            image_no = random.randrange(4)
            enemy_sprite = AsteroidSprite(
                image_list[image_no],
                scale=SCALE,
                type=ASTEROID_TYPE_BIG,
            )

            side = random.randint(0, 3)
            if side == 0:
                enemy_sprite.center_x = -50
                enemy_sprite.center_y = random.uniform(100, WINDOW_HEIGHT - 100)
            elif side == 1:
                enemy_sprite.center_x = WINDOW_WIDTH + 50
                enemy_sprite.center_y = random.uniform(100, WINDOW_HEIGHT - 100)
            elif side == 2:
                enemy_sprite.center_x = random.uniform(100, WINDOW_WIDTH - 100)
                enemy_sprite.center_y = WINDOW_HEIGHT + 50
            else:
                enemy_sprite.center_x = random.uniform(100, WINDOW_WIDTH - 100)
                enemy_sprite.center_y = -50

            speed_mult = 1.0
            if self.difficulty == DIFFICULTY_EASY:
                speed_mult = 0.7
            elif self.difficulty == DIFFICULTY_HARD:
                speed_mult = 1.5

            enemy_sprite.change_x = random.uniform(-3.5, 3.5) * speed_mult
            enemy_sprite.change_y = random.uniform(-3.5, 3.5) * speed_mult
            enemy_sprite.change_angle = random.uniform(-2.5, 2.5) * speed_mult
            self.asteroid_list.append(enemy_sprite)

        self.text_score = arcade.Text(
            f"СЧЕТ: {self.score}",
            x=20,
            y=WINDOW_HEIGHT - 40,
            font_size=20,
            color=arcade.color.WHITE,
            bold=True
        )
        self.text_asteroid_count = arcade.Text(
            f"АСТЕРОИДОВ: {len(self.asteroid_list)}",
            x=20,
            y=WINDOW_HEIGHT - 70,
            font_size=16,
            color=arcade.color.LIGHT_GRAY
        )

    def update_life_display(self):
        self.ship_life_list = arcade.SpriteList()
        cur_pos = 30

        for i in range(int(self.lives)):
            life = arcade.Sprite(
                ":resources:images/space_shooter/playerLife1_orange.png",
                scale=SCALE,
            )
            life.angle = 0
            life.center_x = cur_pos + life.width / 2
            life.center_y = 30
            cur_pos += life.width + 10
            self.ship_life_list.append(life)

        if self.lives % 1 > 0.1:
            life = arcade.Sprite(
                ":resources:images/space_shooter/playerLife1_orange.png",
                scale=SCALE * 0.7,
            )
            life.angle = 0
            life.center_x = cur_pos + life.width / 2
            life.center_y = 30
            life.alpha = 128
            self.ship_life_list.append(life)

    def activate_super_attack(self):
        """Активирует супер-атаку - взрывная волна"""
        self.super_attack_ready = False
        self.super_attack_cooldown = self.super_attack_cooldown_max
        explosion_radius = 300

        arcade.play_sound(self.super_attack_sound, volume=0.7)

        destroyed_count = 0
        for asteroid in self.asteroid_list:
            distance = math.sqrt(
                (asteroid.center_x - self.player_sprite.center_x)**2 +
                (asteroid.center_y - self.player_sprite.center_y)**2
            )
            if distance < explosion_radius:
                self.split_asteroid(cast(AsteroidSprite, asteroid))
                asteroid.remove_from_sprite_lists()
                self.score += 100
                destroyed_count += 1

        self.super_attack_effect_timer = 30

        if destroyed_count >= 5 and self.voice_mega_kill:
            arcade.play_sound(self.voice_mega_kill, volume=0.5)

    def next_wave(self):
        """Переход на следующий уровень"""
        self.current_wave += 1
        self.asteroids_destroyed_this_wave = 0
        self.asteroids_needed_for_next_wave = 5 + self.current_wave * 2

        spawn_count = 3 + self.current_wave
        image_list = (
            ":resources:images/space_shooter/meteorGrey_big1.png",
            ":resources:images/space_shooter/meteorGrey_big2.png",
            ":resources:images/space_shooter/meteorGrey_big3.png",
            ":resources:images/space_shooter/meteorGrey_big4.png",
        )

        for _ in range(spawn_count):
            image_no = random.randrange(4)
            enemy_sprite = AsteroidSprite(
                image_list[image_no],
                scale=SCALE,
                type=ASTEROID_TYPE_BIG,
            )

            side = random.randint(0, 3)
            if side == 0:
                enemy_sprite.center_x = -50
                enemy_sprite.center_y = random.uniform(100, WINDOW_HEIGHT - 100)
            elif side == 1:
                enemy_sprite.center_x = WINDOW_WIDTH + 50
                enemy_sprite.center_y = random.uniform(100, WINDOW_HEIGHT - 100)
            elif side == 2:
                enemy_sprite.center_x = random.uniform(100, WINDOW_WIDTH - 100)
                enemy_sprite.center_y = WINDOW_HEIGHT + 50
            else:
                enemy_sprite.center_x = random.uniform(100, WINDOW_WIDTH - 100)
                enemy_sprite.center_y = -50

            speed_mult = 1.0 + (self.current_wave * 0.1)
            enemy_sprite.change_x = random.uniform(-3.5, 3.5) * speed_mult
            enemy_sprite.change_y = random.uniform(-3.5, 3.5) * speed_mult
            enemy_sprite.change_angle = random.uniform(-2.5, 2.5) * speed_mult
            self.asteroid_list.append(enemy_sprite)

        self.wave_transition_timer = 60
        self.wave_active = True
        arcade.play_sound(self.hit_sound1, volume=0.3)
        print(f"⚡ УРОВЕНЬ {self.current_wave}! Нужно уничтожить: {self.asteroids_needed_for_next_wave} астероидов")

    def on_draw(self):
        self.clear()
        current_time = time.time()

        # Фон
        if self.player_sprite:
            self.background_manager.draw(
                current_time,
                self.player_sprite.change_x,
                self.player_sprite.change_y
            )
        else:
            self.background_manager.draw(current_time)

        # Спрайты
        self.asteroid_list.draw()
        self.bullet_list.draw()
        self.player_sprite_list.draw()
        self.ship_life_list.draw()

        # Текст
        if self.text_score:
            self.text_score.draw()
        if self.text_asteroid_count:
            self.text_asteroid_count.draw()

        # Информация в правом верхнем углу
        arcade.draw_text(
            f"👤 {self.nickname}",
            WINDOW_WIDTH - 20,
            WINDOW_HEIGHT - 40,
            arcade.color.CYAN,
            20,
            anchor_x="right",
            bold=True
        )

        arcade.draw_text(
            f"❤️ {self.lives}/{self.max_lives}",
            WINDOW_WIDTH - 20,
            WINDOW_HEIGHT - 70,
            arcade.color.RED if self.lives < self.max_lives / 2 else arcade.color.WHITE,
            16,
            anchor_x="right"
        )

        # ОТОБРАЖЕНИЕ УРОВНЯ
        wave_text = f"🌊 УРОВЕНЬ {self.current_wave}"
        wave_color = arcade.color.CYAN

        if self.wave_transition_timer > 0:
            self.wave_transition_timer -= 1
            pulse = math.sin(current_time * 10) * 0.3 + 0.7
            wave_color = (255, 215, 0, int(255 * pulse))
            wave_text = f"⚡ УРОВЕНЬ {self.current_wave} ⚡"

        arcade.draw_text(
            wave_text,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - 100,
            wave_color,
            36,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Прогресс-бар уровня
        progress = self.asteroids_destroyed_this_wave / self.asteroids_needed_for_next_wave
        progress = min(1.0, progress)

        arcade.draw_lbwh_rectangle_outline(
            WINDOW_WIDTH / 2 - 200,
            WINDOW_HEIGHT - 150,
            400, 20,
            arcade.color.WHITE, 2
        )

        arcade.draw_lbwh_rectangle_filled(
            WINDOW_WIDTH / 2 - 200,
            WINDOW_HEIGHT - 150,
            400 * progress, 20,
            arcade.color.GREEN if progress < 0.7 else arcade.color.ORANGE if progress < 0.9 else arcade.color.RED
        )

        arcade.draw_text(
            f"{self.asteroids_destroyed_this_wave}/{self.asteroids_needed_for_next_wave}",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - 180,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center"
        )

        # Индикатор супер-атаки
        if not self.super_attack_ready:
            cooldown_percent = self.super_attack_cooldown / self.super_attack_cooldown_max
            arcade.draw_lbwh_rectangle_filled(
                WINDOW_WIDTH // 2 - 100,
                WINDOW_HEIGHT - 50,
                200 * (1 - cooldown_percent), 20,
                arcade.color.GRAY
            )
            arcade.draw_text(
                f"⏳ СУПЕР-АТАКА: {self.super_attack_cooldown // 60 + 1}с",
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT - 70,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center"
            )
        else:
            pulse = math.sin(current_time * 5) * 0.2 + 0.8
            arcade.draw_lbwh_rectangle_filled(
                WINDOW_WIDTH // 2 - 100,
                WINDOW_HEIGHT - 50,
                200, 20,
                (255, 215, 0, int(255 * pulse))
            )
            arcade.draw_text(
                "⚡ СУПЕР-АТАКА ГОТОВА! [C] ⚡",
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT - 70,
                arcade.color.GOLD,
                16,
                anchor_x="center",
                bold=True
            )

        # Эффект супер-атаки
        if self.super_attack_effect_timer > 0:
            self.super_attack_effect_timer -= 1
            alpha = int(self.super_attack_effect_timer * 8)
            arcade.draw_circle_outline(
                self.player_sprite.center_x,
                self.player_sprite.center_y,
                300,
                (255, 215, 0, alpha),
                5
            )

        # Комбо
        if self.combo > 1:
            pulse = math.sin(current_time * 10) * 0.1 + 0.9
            size = 36 + int(10 * (1 - pulse))

            if self.combo >= 20:
                combo_color = arcade.color.PURPLE
            elif self.combo >= 10:
                combo_color = arcade.color.RED
            elif self.combo >= 5:
                combo_color = arcade.color.ORANGE
            else:
                combo_color = arcade.color.YELLOW

            arcade.draw_text(
                f"{self.combo}x КОМБО!",
                WINDOW_WIDTH / 2,
                WINDOW_HEIGHT / 2 + 200,
                combo_color,
                size,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name=("Arial Rounded MT Bold", "Arial", "Helvetica")
            )

            if self.combo_multiplier > 1:
                arcade.draw_text(
                    f"x{self.combo_multiplier} ОЧКОВ!",
                    WINDOW_WIDTH / 2,
                    WINDOW_HEIGHT / 2 + 160,
                    arcade.color.GREEN,
                    24,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )

            if self.combo_timer > 0:
                timer_width = 200 * (self.combo_timer / 60)
                arcade.draw_lbwh_rectangle_filled(
                    WINDOW_WIDTH / 2 - 100,
                    WINDOW_HEIGHT / 2 + 140,
                    timer_width, 5,
                    combo_color
                )

        # Счетчик убийств
        if self.kill_streak >= 5:
            arcade.draw_text(
                f"🔥 {self.kill_streak} УБИЙСТВ",
                WINDOW_WIDTH - 20,
                WINDOW_HEIGHT - 120,
                arcade.color.ORANGE,
                14,
                anchor_x="right",
                bold=True
            )

        if not self.game_over:
            arcade.draw_text(
                "← → ПОВОРОТ | ↑ ↓ ТЯГА | ПРОБЕЛ ОГОНЬ | C - СУПЕР",
                WINDOW_WIDTH - 20,
                20,
                arcade.color.GRAY,
                14,
                anchor_x="right"
            )
            arcade.draw_text(
                f"⚡ {DIFFICULTY_NAMES[self.difficulty]}",
                WINDOW_WIDTH - 20,
                45,
                DIFFICULTY_COLORS[self.difficulty],
                14,
                anchor_x="right",
                bold=True
            )
            arcade.draw_text(
                f"🔥 {self.max_combo}x",
                WINDOW_WIDTH - 20,
                70,
                arcade.color.YELLOW,
                14,
                anchor_x="right"
            )
            arcade.draw_text(
                f"{BACKGROUND_NAMES[self.background_manager.current_background]}",
                WINDOW_WIDTH - 20,
                95,
                arcade.color.CYAN,
                12,
                anchor_x="right"
            )

    def on_key_press(self, symbol, modifiers):
        if self.game_over or self.player_sprite.respawning:
            return

        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = -TURN_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = TURN_SPEED
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = THRUST_AMOUNT
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = -THRUST_AMOUNT
        elif symbol == arcade.key.SPACE:
            bullet_sprite = TurningSprite(
                ":resources:images/space_shooter/laserBlue01.png",
                scale=SCALE * 1.3
            )
            bullet_speed = 13
            angle_radians = math.radians(self.player_sprite.angle)
            bullet_sprite.change_y = math.cos(angle_radians) * bullet_speed
            bullet_sprite.change_x = math.sin(angle_radians) * bullet_speed

            ship_radius = max(self.player_sprite.width, self.player_sprite.height) / 2
            bullet_offset = ship_radius + bullet_sprite.height / 2
            bullet_sprite.center_x = self.player_sprite.center_x + math.sin(angle_radians) * bullet_offset
            bullet_sprite.center_y = self.player_sprite.center_y + math.cos(angle_radians) * bullet_offset

            self.bullet_list.append(bullet_sprite)
            bullet_sprite.update()
            arcade.play_sound(self.laser_sound, speed=random.uniform(0.8, 1.2))

        elif symbol == arcade.key.C:
            if self.super_attack_ready and not self.player_sprite.respawning:
                self.activate_super_attack()
        elif symbol == arcade.key.B:
            self.background_manager.next_background()
        elif symbol == arcade.key.V:
            self.background_manager.prev_background()
        elif symbol == arcade.key.R:
            self.setup(self.background_manager, self.difficulty, self.nickname)
        elif symbol == arcade.key.ESCAPE:
            from views.menu_view import MenuView
            menu = MenuView()
            self.window.show_view(menu)

    def on_key_release(self, symbol, modifiers):
        if symbol in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid: AsteroidSprite):
        x = asteroid.center_x
        y = asteroid.center_y

        # СЧЕТЧИК УРОВНЯ
        self.asteroids_destroyed_this_wave += 1

        # Проверка перехода на следующий уровень
        if self.asteroids_destroyed_this_wave >= self.asteroids_needed_for_next_wave:
            self.next_wave()

        self.combo += 1
        self.combo_timer = 60
        self.kill_streak += 1

        if self.combo > self.max_combo:
            self.max_combo = self.combo

        # ГОЛОСОВОЙ АНОНСЕР
        current_time = time.time()
        if self.kill_streak >= 20 and current_time - self.last_announcement > 2:
            if self.voice_mega_kill:
                arcade.play_sound(self.voice_mega_kill, volume=0.5)
            self.last_announcement = current_time
        elif self.kill_streak >= 10 and current_time - self.last_announcement > 2:
            if self.voice_perfect:
                arcade.play_sound(self.voice_perfect, volume=0.5)
            self.last_announcement = current_time

        # Определение множителя комбо
        if self.combo >= 20:
            self.combo_multiplier = 4
            combo_bonus = 40
        elif self.combo >= 10:
            self.combo_multiplier = 3
            combo_bonus = 30
        elif self.combo >= 5:
            self.combo_multiplier = 2
            combo_bonus = 20
        else:
            self.combo_multiplier = 1
            combo_bonus = 10

        # Базовые очки
        if asteroid.type == ASTEROID_TYPE_BIG:
            base_score = 20
        elif asteroid.type == ASTEROID_TYPE_MEDIUM:
            base_score = 50
        elif asteroid.type == ASTEROID_TYPE_SMALL:
            base_score = 100
        else:
            base_score = 0

        self.score += int(base_score * self.combo_multiplier) + combo_bonus

        # Разделение астероида
        if asteroid.type == ASTEROID_TYPE_BIG:
            for _ in range(3):
                image_no = random.randrange(2)
                image_list = [
                    ":resources:images/space_shooter/meteorGrey_med1.png",
                    ":resources:images/space_shooter/meteorGrey_med2.png"
                ]
                enemy_sprite = AsteroidSprite(
                    image_list[image_no],
                    scale=SCALE * 1.1,
                    type=ASTEROID_TYPE_MEDIUM
                )
                enemy_sprite.center_x = x + random.uniform(-10, 10)
                enemy_sprite.center_y = y + random.uniform(-10, 10)
                enemy_sprite.change_x = random.uniform(-4.5, 4.5)
                enemy_sprite.change_y = random.uniform(-4.5, 4.5)
                enemy_sprite.change_angle = random.uniform(-3, 3)
                self.asteroid_list.append(enemy_sprite)
            arcade.play_sound(self.hit_sound1, volume=0.6)

        elif asteroid.type == ASTEROID_TYPE_MEDIUM:
            for _ in range(3):
                image_no = random.randrange(2)
                image_list = [
                    ":resources:images/space_shooter/meteorGrey_small1.png",
                    ":resources:images/space_shooter/meteorGrey_small2.png"
                ]
                enemy_sprite = AsteroidSprite(
                    image_list[image_no],
                    scale=SCALE * 1.0,
                    type=ASTEROID_TYPE_SMALL
                )
                enemy_sprite.center_x = x + random.uniform(-8, 8)
                enemy_sprite.center_y = y + random.uniform(-8, 8)
                enemy_sprite.change_x = random.uniform(-5.5, 5.5)
                enemy_sprite.change_y = random.uniform(-5.5, 5.5)
                enemy_sprite.change_angle = random.uniform(-4, 4)
                self.asteroid_list.append(enemy_sprite)
            arcade.play_sound(self.hit_sound2, volume=0.5)

        elif asteroid.type == ASTEROID_TYPE_SMALL:
            arcade.play_sound(self.hit_sound3, volume=0.4)

    def on_update(self, delta_time):
        if not self.game_over:
            self.asteroid_list.update()
            self.bullet_list.update()
            self.player_sprite_list.update()

            # Таймер комбо
            if self.combo_timer > 0:
                self.combo_timer -= 1
                if self.combo_timer <= 0:
                    self.combo = 0
                    self.combo_multiplier = 1
                    self.kill_streak = 0

            # Кулдаун супер-атаки
            if not self.super_attack_ready:
                self.super_attack_cooldown -= 1
                if self.super_attack_cooldown <= 0:
                    self.super_attack_ready = True
                    self.super_attack_cooldown = 0

            # Обновление угла корабля
            if not self.player_sprite.respawning:
                self.player_sprite.angle += self.player_sprite.change_angle
                self.player_sprite.angle %= 360

            # Обработка пуль
            for bullet in self.bullet_list:
                asteroids = arcade.check_for_collision_with_list(bullet, self.asteroid_list)

                for asteroid in asteroids:
                    self.split_asteroid(cast(AsteroidSprite, asteroid))
                    asteroid.remove_from_sprite_lists()
                    bullet.remove_from_sprite_lists()

                # Удаление пуль за экраном
                size = max(bullet.width, bullet.height)
                if (bullet.center_x < -size or bullet.center_x > WINDOW_WIDTH + size or
                        bullet.center_y < -size or bullet.center_y > WINDOW_HEIGHT + size):
                    bullet.remove_from_sprite_lists()

            # Столкновения с кораблем
            if not self.player_sprite.respawning:
                asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)

                if asteroids:
                    asteroid = cast(AsteroidSprite, asteroids[0])
                    damage = ASTEROID_DAMAGE.get(asteroid.type, 1)
                    self.lives -= damage
                    print(f"Попадание! Урон: {damage}, Осталось жизней: {self.lives}")

                    if self.lives > 0:
                        self.update_life_display()
                        self.player_sprite.respawn()
                        self.split_asteroid(asteroid)
                        asteroid.remove_from_sprite_lists()
                        self.combo = 0
                        self.combo_timer = 0
                        self.combo_multiplier = 1
                        self.kill_streak = 0
                    else:
                        self.game_over = True
                        if self.voice_game_over:
                            arcade.play_sound(self.voice_game_over, volume=0.6)
                        print(f"GAME OVER! Score: {self.score}, Max Combo: {self.max_combo}, Wave: {self.current_wave}, Difficulty: {DIFFICULTY_NAMES[self.difficulty]}")
                        self.window.show_view(GameOverView(
                            self.score,
                            self.background_manager,
                            self.difficulty,
                            self.nickname,
                            self.max_combo,
                            self.current_wave
                        ))

            # Обновление текста
            if self.text_score:
                self.text_score.text = f"СЧЕТ: {self.score}"
            if self.text_asteroid_count:
                self.text_asteroid_count.text = f"АСТЕРОИДОВ: {len(self.asteroid_list)}"