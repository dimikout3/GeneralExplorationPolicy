# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame as pg

import sys, os
import numpy as np

from mars_explorer.render.settings import *
from mars_explorer.render.sprites import *

class Viewer():
    def __init__(self,env):
        pg.init()
        self.env = env
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()

        for x, y in env.obstacles_idx:
            Obstacle(self, x, y)
        self.player = Drone(self, env)

    def load_data(self):
        self.drone_img = pg.image.load(DRONE_IMG).convert_alpha()
        self.drone_img = pg.transform.scale(self.drone_img, (TILESIZE, TILESIZE))

        self.obstacle_img = pg.image.load(OBSTACLE_IMG).convert_alpha()
        self.obstacle_img = pg.transform.scale(self.obstacle_img, (TILESIZE, TILESIZE))

        self.bck_img = pg.image.load(BG_IMG).convert_alpha()
        self.bck_img = pg.transform.scale(self.bck_img, (HEIGHT, WIDTH))

        # lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(LIGHT_MASK).convert_alpha()
        # TODO: check radius, image radius is not on edge of the square
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

    def run(self):
        self.update()
        self.draw()

    def quit(self):
        pg.quit()
        # sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

    def render_fog_camera(self):
        # dark everywhere except where the lidar sees every time step
        cameraX = (self.env.x+.5)*TILESIZE
        cameraY = (self.env.y+.5)*TILESIZE

        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = (cameraX, cameraY)
        print(f"light x:{cameraX} y:{cameraY}")

        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def render_fog_explored(self):
        # dark everywhere(unexplored), but light on every explored cell
        explored_idx = np.where(self.env.outputMap > .0)
        explored_x = explored_idx[0]
        explored_y = explored_idx[1]
        explored_idx = np.stack((explored_x, explored_y), axis=1)
        explored_idx = [list(i) for i in explored_idx]

        self.fog.fill(NIGHT_COLOR)

        for x,y in explored_idx:
            cameraX = (x+.5)*TILESIZE
            cameraY = (y+.5)*TILESIZE

            self.light_rect.center = (cameraX, cameraY)

            self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw_lidar_rays(self):
        thetas, ranges = self.env.ldr.thetas, self.env.ldr.ranges
        currentX = self.env.x*TILESIZE+0.5*TILESIZE
        currentY = self.env.y*TILESIZE+0.5*TILESIZE
        xObs = (currentX + TILESIZE*ranges*np.cos(thetas)).astype(float)
        yObs = (currentY + TILESIZE*ranges*np.sin(thetas)).astype(float)
        for x,y in zip(xObs, yObs):
            pg.draw.line(self.screen, RED, (currentX, currentY), (x, y))
            pg.draw.circle(self.screen, RED, (x, y), TILESIZE/8)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.blit(self.bck_img, (0, 0))
        # self.draw_grid()
        self.draw_lidar_rays()
        self.all_sprites.draw(self.screen)
        # self.render_fog_camera()
        self.render_fog_explored()
        pg.display.flip()

    def get_display_as_array(self):
        return pg.surfarray.array3d(self.screen)