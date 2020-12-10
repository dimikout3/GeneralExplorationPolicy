import numpy as np

from mars_explorer.utils.randomMapGenerator import Generator
from mars_explorer.utils.lidarSensor import Lidar
from mars_explorer.render.viewer import Viewer

import gym
from gym import error, spaces, utils
from gym.utils import seeding

DEFAULT_CONFIG={
    #  general configuration for the topology of operational area
    "start":[0,0],
    "size":[42,42],
    #  configuration regarding the movements of uav
    "movementCost":0.2,

    # configuration regarding the random map generation
    # absolute number of obstacles, randomly placed in env
    "obstacles":10,
    # if rows/colums activated the obstacles will be placed in a semi random
    # spacing
    "number_rows":None,
    "number_columns":None,
    # noise activated only when row/columns activated
    "noise":[0,0],
    # margins expressed in cell if rows/columns not activated
    "margins":[1, 1],
    # obstacle size expressed in cell if rows/columns not activated
    "obstacle_size":[2,2]
}