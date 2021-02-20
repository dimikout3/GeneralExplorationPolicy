import gym
import numpy as np
from scipy.spatial import distance
import time
import pygame as pg
import argparse
import matplotlib.pyplot as plt
import json

from mars_explorer.envs.settings import DEFAULT_CONFIG as conf

N_GAMES = 5
N_STEPS = 50
DELAY = 0.2
CONF_PATH = "/home/dkoutras/Documents/IROS2021/42x42/params.json"


def get_conf():

    if CONF_PATH != "":
        conf_json = json.load(open(CONF_PATH,'r'))
        conf = conf_json["env_config"]
        conf["margins"] = [3,3]
    else:
        conf["size"] = [84, 84]
        # conf["obstacles"] = 20
        # conf["lidar_range"] = 4
        # conf["obstacle_size"] = [1,3]

        conf["viewer"]["night_color"] = (0, 0, 0)
        conf["viewer"]["draw_lidar"] = True

    return conf


def find_frontiers(obs):

    free_x, free_y, free_z = np.where(obs == 0.3)
    free_points = np.array(list(zip(free_x, free_y)))

    # diff --> temporal differences
    diff_x = [0,-1,-1,-1,0,1,1,1]
    diff_y = [1,1,0,-1,-1,-1,0,1]

    frontiers = []

    for free_x, free_y in zip(free_x, free_y):

        for dx, dy in zip(diff_x, diff_y):

            test_x = free_x + dx
            test_y = free_y + dy

            if test_x>=0 and test_x<obs.shape[0] and test_y>=0 and test_y<obs.shape[1]:
                if obs[test_x, test_y] == 0:
                    frontiers.append([free_x, free_y])
                    break

    return np.array(frontiers)


def check_collision(distances, canditate_action, obs):

    for index, (x,y) in enumerate(canditate_action):

        if x<0 or y<0 or x>=obs.shape[0] or x>=obs.shape[1]:
            distances[index] = np.inf
        elif obs[x,y] == 1.:
            distances[index] = np.inf

    return distances


def evaluate(frontiers, obs):
    # return the distance from each candiatate action
    canditate_action = [[env.x+1, env.y], # action 0 is right
                        [env.x-1, env.y], # action 1 is left
                        [env.x, env.y+1], # action 2 is down
                        [env.x, env.y-1]] # action 3 is up

    distances = distance.cdist(frontiers, canditate_action)

    evaluation = np.min(distances, axis=0)
    evaluation = check_collision(evaluation, canditate_action, obs)
    return evaluation


def get_action(obs):

    frontiers = find_frontiers(obs)
    evaluate_actions = evaluate(frontiers, obs)

    return np.argmin(evaluate_actions)


def play_game(env):

    total_reward = .0
    obs = env.reset()
    env.render()

    for time_step in range(N_STEPS):

        action = get_action(obs)

        obs, reward, done, info = env.step(action)
        total_reward += reward

        env.render()
        time.sleep(DELAY)

        if done:
            break

    return total_reward


if __name__ == "__main__":
    conf = get_conf()

    env = gym.make('mars_explorer:exploConf-v01', conf=conf)

    for game in range(N_GAMES):
        total_reward = play_game(env)
