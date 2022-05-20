from enum import Enum
from pathlib import Path
from typing import List

import pygame
from pygame.locals import *


# GAME
# set the walking speed to 30 frames per second (example: base char speed 2 is 60 px moving per second)
# same with fighting
GAME_FPS = 60
WALKING_TARGET_FPS = 30
GAME_WALKING_FPS_RATIO = GAME_FPS / WALKING_TARGET_FPS


class MovementType(Enum):
    WALK = 0
    SPRINT = 1


class WalkDirection(Enum):
    NONE = 0
    RIGHT = 1
    DOWN = 2
    UP = 3
    LEFT = 4
    UP_LEFT = 5
    UP_RIGHT = 6
    DOWN_LEFT = 7
    DOWN_RIGHT = 8


class MainChar(pygame.sprite.Sprite):
    # MOVEMENT
    WALK_SPEED = 4
    SPRINT_SPEED = 6
    MAPPED_WALKING = {
        KSCAN_W: "top",
        KSCAN_D: "right",
        KSCAN_A: "left",
        KSCAN_S: "down",
    }

    # STATS
    BASE_HP = 10
    MAX_HP = BASE_HP

    # IMAGE
    IMAGENAME = 'main_char.png'

    _counter = 0

    def __init__(self, pos: List[int], *groups: pygame.sprite.AbstractGroup):
        super().__init__(*groups)

        MainChar._counter += 1
        self.id = MainChar._counter

        self.image = pygame.image.load(Path.cwd() / 'resources' / 'img' / 'chars' / self.IMAGENAME)

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self.walk_direction = WalkDirection.NONE
        self.movement_type = MovementType.WALK

    def get_current_speed(self) -> float:
        """ gets the current movement speed of the character"""

        if self.movement_type is MovementType.SPRINT:
            return self.SPRINT_SPEED / GAME_WALKING_FPS_RATIO
        else:
            return self.WALK_SPEED / GAME_WALKING_FPS_RATIO

    def walk_top(self) -> None:
        self.rect.y = self.rect.y - self.get_current_speed()

    def walk_right(self) -> None:
        self.rect.x = self.rect.x + self.get_current_speed()

    def walk_left(self) -> None:
        self.rect.x = self.rect.x - self.get_current_speed()

    def walk_down(self) -> None:
        self.rect.y = self.rect.y + self.get_current_speed()

    def solve_for_walking(self, name: str):
        """method to find and execute the right walking method based on input"""
        do = f"walk_{name}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            func()


class MainCharGroup(pygame.sprite.GroupSingle):
    sprite: MainChar

    def sprites(self) -> List[MainChar]:
        return [self.sprite]


def create_main_char() -> MainChar:
    char = MainChar([0, 200])

    return char


def create_main_char_group() -> MainCharGroup:
    char = create_main_char()
    group = MainCharGroup(char)

    return group
