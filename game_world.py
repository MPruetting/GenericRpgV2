from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List, Optional

import pygame
from pygame.locals import *

from menu import SCREEN_SIZE, GAME_WINDOW

# GAME
# set the walking speed to 30 frames per second (example: base char speed 2 is 60 px moving per second)
# same with fighting
GAME_FPS = 60
WALKING_TARGET_FPS = 30
GAME_WALKING_FPS_RATIO = GAME_FPS / WALKING_TARGET_FPS


class GameStage:
    def __init__(
            self,
            sprite_group: MainCharGroup = None,
            name: str = "Stage"
    ):
        self.sprite_group = sprite_group
        self.name = name
        self.font_surface = self.set_font()

        self._top_stage: Optional[GameStage] = None
        self._bottom_stage: Optional[GameStage] = None
        self._right_stage: Optional[GameStage] = None
        self._left_stage: Optional[GameStage] = None

    @property
    def top_stage(self) -> Optional[GameStage]:
        return self._top_stage

    @top_stage.setter
    def top_stage(self, stage: GameStage):
        self._top_stage = stage
        stage.bottom_stage = self

    @property
    def bottom_stage(self) -> Optional[GameStage]:
        return self._bottom_stage

    @bottom_stage.setter
    def bottom_stage(self, stage: GameStage):
        self._bottom_stage = stage
        stage.top_stage = self

    @property
    def right_stage(self) -> Optional[GameStage]:
        return self._right_stage

    @right_stage.setter
    def right_stage(self, stage: GameStage):
        self._right_stage = stage
        self.left_stage = self

    @property
    def left_stage(self) -> Optional[GameStage]:
        return self._left_stage

    @left_stage.setter
    def left_stage(self, stage: GameStage):
        self._left_stage = stage
        self.right_stage = self

    def set_font(self) -> pygame.Surface:
        """Sets font and returns a text surface"""
        font = pygame.font.SysFont("Arial", 40)
        return font.render(self.name, True, pygame.color.Color("blue"))

    def draw_page_name(self) -> None:
        """Draws the page name on top of the window"""
        GAME_WINDOW.blit(
            self.font_surface,
            [
                GAME_WINDOW.get_width() / 2 - self.font_surface.get_width() / 2,
                10
            ]
        )


class GameWorld:
    def __init__(self, stages: List[GameStage]):
        self.stages = stages
        self.current_stage = self.stages[0]


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

    def solve_for_walking(self, name: str) -> None:
        """method to find and execute the right walking method based on input"""
        if self.wall_collision_check():
            return None
        do = f"walk_{name}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            func()

    def wall_collision_check(self) -> bool:
        """ if next move will hit a wall, return true """
        speed = self.get_current_speed()

        if self.rect.bottomright[0] + speed > SCREEN_SIZE[0] and pygame.key.get_pressed()[K_d]:
            return True
        if self.rect.bottomright[1] + speed > SCREEN_SIZE[1] and pygame.key.get_pressed()[K_s]:
            return True
        if self.rect.x - speed < 0 and pygame.key.get_pressed()[K_a]:
            return True
        if self.rect.y - speed < 0 and pygame.key.get_pressed()[K_w]:
            return True
        return False


class MainCharGroup(pygame.sprite.GroupSingle):
    sprite: MainChar

    def sprites(self) -> List[MainChar]:
        return [self.sprite]


def create_stages() -> List[GameStage]:
    """Creates the stages for the game"""
    main_char_group = create_main_char_group()
    start_stage = GameStage(main_char_group, "Start Level")
    return [start_stage]


def create_game_world() -> GameWorld:
    stages = create_stages()
    return GameWorld(stages)


def create_main_char() -> MainChar:
    char = MainChar([0, 200])

    return char


def create_main_char_group() -> MainCharGroup:
    char = create_main_char()
    group = MainCharGroup(char)

    return group
