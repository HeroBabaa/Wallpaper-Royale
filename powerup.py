import pygame
from pygame.locals import *
import random
import math
import os
from PIL import Image
import ctypes
import json


with open("config.json") as json_config_file:
    config = json.load(json_config_file)
    json_config_file.close()


# Colors and fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Color for the power-up
GREEN = (0, 255, 0)  # Color for the power-up
BLUE = (0, 0, 255)  # Color for the power-up
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

base_font_size = 36  # Base font size


# Power-up settings
POWER_UP_RADIUS = config['power_up_settings']['POWER_UP_RADIUS']
POWER_UP_SPAWN_RATE = config['power_up_settings']['POWER_UP_SPAWN_RATE']  # Frames before a power-up spawns (1 per 60 frames ~ 1 per second)
MAX_POWER_UP_COUNT = config['power_up_settings']['MAX_POWER_UP_COUNT']


VEL_X_MULT = config['power_up_settings']['VEL_X_MULT']
VEL_Y_MULT = config['power_up_settings']['VEL_Y_MULT']
SCALE_INCREASE_AMOUNT = config['power_up_settings']['SCALE_INCREASE_AMOUNT']
POWER_UP_HEALTH_INCREASE = config['power_up_settings']['POWER_UP_HEALTH_INCREASE']
INVINCIBLE_POWER_UP_DURATION = config['power_up_settings']['INVINCIBLE_POWER_UP_DURATION']
INVINCIBLE_SHIELD_RADIUS = config['power_up_settings']['INVINCIBLE_SHIELD_RADIUS']
DUPE_RADIUS_RATIO = config['power_up_settings']['DUPE_RADIUS_RATIO']




POWER_UP_TYPE_COUNT = 5
SPEED_POWER_UP = 0
SCALE_POWER_UP = 1
HEALTH_POWER_UP = 2
INVINCIBLE_POWER_UP = 3
DUPE_POWER_UP = 4

# Power-up spawn probabilities (IDs mapped to spawn chances)
POWER_UP_TYPES = {
    SPEED_POWER_UP: config['power_up_settings']['SPEED_POWER_UP_WEIGHT'],       
    SCALE_POWER_UP: config['power_up_settings']['SCALE_POWER_UP_WEIGHT'],       
    HEALTH_POWER_UP: config['power_up_settings']['HEALTH_POWER_UP_WEIGHT'],      
    INVINCIBLE_POWER_UP: config['power_up_settings']['INVINCIBLE_POWER_UP_WEIGHT'],  
    DUPE_POWER_UP: config['power_up_settings']['DUPE_POWER_UP_WEIGHT']          
}

# Pre-compute lists for `random.choices` using the IDs and their weights
power_up_ids = list(POWER_UP_TYPES.keys())
power_up_weights = list(POWER_UP_TYPES.values())





class PowerUp:
    """Power-up object to increase circle speed."""
    def __init__(self, x, y, power_up_type):
        self.x = x
        self.y = y
        self.power_up_type = power_up_type
        if (power_up_type == SPEED_POWER_UP): self.color = BLUE
        elif (power_up_type == SCALE_POWER_UP): self.color = RED
        elif (power_up_type == HEALTH_POWER_UP): self.color = GREEN
        elif (power_up_type == INVINCIBLE_POWER_UP): self.color = YELLOW
        elif (power_up_type == DUPE_POWER_UP): self.color = PURPLE

    def draw(self, surface):
        """Draw the power-up."""
        pygame.draw.circle(surface, self.color, (self.x, self.y), POWER_UP_RADIUS)

    def use_power_up(self, circle, circles):
        if (self.power_up_type == SPEED_POWER_UP): circle.increase_speed()
        elif (self.power_up_type == SCALE_POWER_UP): circle.increase_scale(SCALE_INCREASE_AMOUNT)
        elif (self.power_up_type == HEALTH_POWER_UP): circle.add_health_percentage(POWER_UP_HEALTH_INCREASE)
        elif (self.power_up_type == INVINCIBLE_POWER_UP): circle.give_invincible(INVINCIBLE_POWER_UP_DURATION)
        elif (self.power_up_type == DUPE_POWER_UP): return "dupe"
            
        

