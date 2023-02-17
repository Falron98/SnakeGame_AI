import sys
from enum import Enum
from random import randrange

import numpy as np
import pygame as pg

vec2 = pg.math.Vector2


class SnakeGame:
    def __init__(self):
        pg.init()
        self.WINDOW = 1000
        self.TILE_SIZE = 40
        self.screen = pg.display.set_mode([self.WINDOW] * 2)

        self.clock = pg.time.Clock()

        self.game_over = False
        self.score = 0
        self.reward = 0

        self.new_game()

    def draw_grid(self):
        [pg.draw.line(self.screen, [self.TILE_SIZE] * 3, (x, 0), (x, self.WINDOW)) for x in
         range(0, self.WINDOW, self.TILE_SIZE)]
        [pg.draw.line(self.screen, [self.TILE_SIZE] * 3, (0, y), (self.WINDOW, y)) for y in
         range(0, self.WINDOW, self.TILE_SIZE)]

    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    pg.quit()
                    sys.exit()
            self.snake.control(event)

    def new_game(self):
        self.snake = Snake(self)
        self.food = Food(self)

    def update(self):
        self.snake.update()
        pg.display.flip()
        self.clock.tick(60)

    def draw(self):
        self.screen.fill('black')
        self.draw_grid()
        self.food.draw()
        self.snake.draw()

    def run(self):
        self.process_events()
        self.update()
        self.draw()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class Snake:
    def __init__(self, game):
        self.game = game
        self.size = game.TILE_SIZE
        self.rect = pg.rect.Rect([0, 0, game.TILE_SIZE - 2, game.TILE_SIZE - 2])
        self.rect.center = self.get_random_pos()
        self.direction = vec2(0, 0)
        self.step_delay = 100
        self.time = 0
        self.frame_iter = 0
        self.length = 1
        self.segments = []
        self.direct = Direction.RIGHT
        self.dirs = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 1, pg.K_d: 1}

    def control(self, action):
        self.clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        self.idx = self.clock_wise.index(self.direct)
        if np.array_equal(action, [1, 0, 0]):
            new_dir = self.clock_wise[self.idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (self.idx + 1) % 4
            new_dir = self.clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (self.idx - 1) % 4
            new_dir = self.clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direct = new_dir

        if self.direct == Direction.RIGHT:
            self.direction = vec2(self.size, 0)
        elif self.direct == Direction.LEFT:
            self.direction = vec2(-self.size, 0)
        elif self.direct == Direction.DOWN:
            self.direction = vec2(0, self.size)
        elif self.direct == Direction.UP:
            self.direction = vec2(0, -self.size)

    def check_borders(self):
        if self.rect.left < 0 or self.rect.right > self.game.WINDOW or self.rect.top < 0 or self.rect.bottom > self.game.WINDOW or self.frame_iter > 100*self.length:
            self.game.new_game()
            self.game.game_over = True
            self.game.score = 0
            self.game.reward = -10
            return self.game.game_over, self.game.reward

    def check_food(self):
        if self.rect.center == self.game.food.rect.center:
            self.game.food.rect.center = self.get_random_pos()
            self.game.score += 1
            self.game.reward = 10
            self.length += 1

    def check_selfeating(self):
        if len(self.segments) != len(set(segment.center for segment in self.segments)):
            self.game.new_game()

    def delta_time(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time > self.step_delay:
            self.time = time_now
            return True
        return False

    def move(self):
        if self.delta_time():
            self.frame_iter += 1
            self.rect.move_ip(self.direction)
            self.segments.append(self.rect.copy())
            self.segments = self.segments[-self.length:]

    def get_random_pos(self):
        return [randrange(self.size // 2, self.game.WINDOW - self.size // 2, self.size)] * 2

    def update(self):
        self.check_selfeating()
        self.check_food()
        self.check_borders()
        self.move()

    def get_snake_pos(self):
        return self.rect.center

    def draw(self):
        [pg.draw.rect(self.game.screen, 'green', segment) for segment in self.segments]


class Food:
    def __init__(self, game):
        self.game = game
        self.size = game.TILE_SIZE
        self.rect = pg.rect.Rect([0, 0, game.TILE_SIZE - 2, game.TILE_SIZE - 2])
        self.rect.center = self.game.snake.get_random_pos()

    def draw(self):
        pg.draw.rect(self.game.screen, 'red', self.rect)


if __name__ == "__main__":
    game = SnakeGame()

    while True:
        game.run()
        game_over = game.snake.check_borders()

        if game_over is not None:
            reward = game_over[1]
            game_over = game_over[0]

"""        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w and self.dirs[pg.K_w]:
                self.direction = vec2(0, -self.size)
                self.dirs = {pg.K_w: 1, pg.K_s: 0, pg.K_a: 1, pg.K_d: 1}
            if event.key == pg.K_s and self.dirs[pg.K_s]:
                self.direction = vec2(0, self.size)
                self.dirs = {pg.K_w: 0, pg.K_s: 1, pg.K_a: 1, pg.K_d: 1}
            if event.key == pg.K_d and self.dirs[pg.K_d]:
                self.direction = vec2(self.size, 0)
                self.dirs = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 0, pg.K_d: 1}
            if event.key == pg.K_a and self.dirs[pg.K_a]:
                self.direction = vec2(-self.size, 0)
                self.dirs = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 1, pg.K_d: 0}
        print(self.direction)"""