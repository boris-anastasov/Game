import pyxel
import random
import math


class Background:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles = [[random.choice([(16, 0), (16, 8), (24, 8)]) for _ in range(width // tile_size)] for _ in range(height // tile_size)]

    def draw(self):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                tile_id = self.tiles[y][x]
                pyxel.blt(x * self.tile_size, y * self.tile_size, 0, tile_id[0], tile_id[1], self.tile_size, self.tile_size, 0)


class Sight:
    def __init__(self):
        self.size = 1

    def update(self):
        pass

    def draw(self):
        pyxel.circ(pyxel.mouse_x, pyxel.mouse_y, self.size, 0)


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 4
        self.active = True

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        if self.x < 0 or self.x > pyxel.width or self.y < 0 or self.y > pyxel.height:
            self.active = False

    def draw(self):
        pyxel.circ(self.x, self.y, 1, 2)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.active = True
        self.speed = 0.5
        self.direction = "down"

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y

        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance
        else:
            direction_x = 0
            direction_y = 0

        self.x += direction_x * self.speed
        self.y += direction_y * self.speed

        if abs(dx) > abs(dy):
            if dx > 0:
                self.direction = "right"
            else:
                self.direction = "left"
        else:
            if dy > 0:
                self.direction = "down"
            else:
                self.direction = "up"

    def draw(self):
        if self.direction == "up":
            pyxel.blt(self.x, self.y, 0, 8, 24, self.w, self.h)
        elif self.direction == "down":
            pyxel.blt(self.x, self.y, 0, 0, 16, self.w, self.h)
        elif self.direction == "left":
            pyxel.blt(self.x, self.y, 0, 8, 16, self.w, self.h)
        elif self.direction == "right":
            pyxel.blt(self.x, self.y, 0, 0, 24, self.w, self.h)


class Player:
    def __init__(self, x, y):
        self.direction = None
        self.x = x
        self.y = y
        self.speed = 1
        self.w = 8
        self.h = 8
        self.direction = "down"
        self.magazine = 6

    def update(self):
        if pyxel.btn(pyxel.KEY_W):
            self.y -= self.speed
            self.direction = "up"
        elif pyxel.btn(pyxel.KEY_S):
            self.y += self.speed
            self.direction = "down"
        if pyxel.btn(pyxel.KEY_A):
            self.x -= self.speed
            self.direction = "left"
        elif pyxel.btn(pyxel.KEY_D):
            self.x += self.speed
            self.direction = "right"

        if self.magazine == 0 and pyxel.btnp(pyxel.KEY_R):
            self.magazine = 6

    def draw(self):
        if self.direction == "up":
            pyxel.blt(self.x, self.y, 0, 8, 8, self.w, self.h)
        elif self.direction == "down":
            pyxel.blt(self.x, self.y, 0, 0, 0, self.w, self.h)
        elif self.direction == "left":
            pyxel.blt(self.x, self.y, 0, 8, 0, self.w, self.h)
        elif self.direction == "right":
            pyxel.blt(self.x, self.y, 0, 0, 8, self.w, self.h)

    def shoot(self):
        if self.magazine > 0:
            angle = math.atan2(pyxel.mouse_y - self.y, pyxel.mouse_x - self.x)
            self.magazine -= 1
            return Bullet(self.x, self.y, angle)


class App:
    def __init__(self):
        pyxel.init(160, 120)
        pyxel.load("player.pyxres")
        self.background = Background(160, 120, 8)
        self.player = Player(5, 10)
        self.game_state = "start"
        self.bullets = []
        self.enemies = []
        self.sight = Sight()
        self.score = 0
        self.player_lives = 3
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.game_state == "start":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.game_state = "play"
        elif self.game_state == "play":
            self.player.update()
            self.sight.update()
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                bullet = self.player.shoot()
                if bullet is not None:
                    self.bullets.append(bullet)

            for bullet in self.bullets:
                bullet.update()
                if not bullet.active:
                    self.bullets.remove(bullet)

            for enemy in self.enemies:
                enemy.update(self.player)

                for bullet in self.bullets:
                    if enemy.x < bullet.x < enemy.x + enemy.w and enemy.y < bullet.y < enemy.y + enemy.h:
                        enemy.active = False
                        bullet.active = False
                        self.score += 1

                if (
                    self.player.x + self.player.w > enemy.x
                    and self.player.x < enemy.x + enemy.w
                    and self.player.y + self.player.h > enemy.y
                    and self.player.y < enemy.y + enemy.h
                ):
                    self.player_lives -= 1
                    enemy.active = False
                    if self.player_lives <= 0:
                        self.game_state = "end"

            self.enemies = [enemy for enemy in self.enemies if enemy.active]

            if pyxel.frame_count % 60 == 0:
                enemy_x = random.randint(0, pyxel.width - 8)
                enemy_y = random.randint(0, pyxel.height - 8)
                self.enemies.append(Enemy(enemy_x, enemy_y))

            if self.score >= 6:
                self.game_state = "end"

        elif self.game_state == "end":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.score = 0
                self.player_lives = 3
                self.game_state = "start"

    def draw(self):
        if self.game_state == "start":
            pyxel.cls(0)
            pyxel.text(40, 50, "Press SPACE to start", 7)
        elif self.game_state == "play":
            self.background.draw()

            for enemy in self.enemies:
                enemy.draw()

            self.player.draw()

            for bullet in self.bullets:
                bullet.draw()

            self.sight.draw()

            pyxel.text(5, 5, f"Bullets: {self.player.magazine}", 7)
            pyxel.text(5, 15, f"Score: {self.score}", 7)
            pyxel.text(5, 25, f"Lives: {self.player_lives}", 7)

        elif self.game_state == "end":
            pyxel.cls(0)
            pyxel.text(40, 50, "The forest got occupied!", 7)


App()
