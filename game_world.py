from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import pygame
from pygame.locals import *

from menu import SCREEN_SIZE, GAME_WINDOW

# GAME
# set the walking speed to 30 frames per second (example: base char speed 2 is 60 px moving per second)
# same with fighting
from models import DataModel

GAME_FPS = 60
WALKING_TARGET_FPS = 45
GAME_WALKING_FPS_RATIO = GAME_FPS / WALKING_TARGET_FPS


class GameStage:
    def __init__(
            self,
            sprite_group: MainCharGroup = None,
            name: str = "Stage"
    ):
        self.sprite_group = sprite_group
        self.name = name
        self.coordinates = [0, 0]

        self._top_stage: Optional[GameStage] = None
        self._bottom_stage: Optional[GameStage] = None
        self._right_stage: Optional[GameStage] = None
        self._left_stage: Optional[GameStage] = None

        self.font_surface = self.set_font()

    @property
    def top_stage(self) -> Optional[GameStage]:
        return self._top_stage

    @top_stage.setter
    def top_stage(self, stage: GameStage):
        self._top_stage = stage
        if not stage.bottom_stage:
            stage.bottom_stage = self
            stage.coordinates[1] = self._top_stage.coordinates[1] - 1

    @property
    def bottom_stage(self) -> Optional[GameStage]:
        return self._bottom_stage

    @bottom_stage.setter
    def bottom_stage(self, stage: GameStage):
        self._bottom_stage = stage
        if not stage.top_stage:
            stage.top_stage = self
            stage.coordinates[1] = self._bottom_stage.coordinates[1] + 1

    @property
    def right_stage(self) -> Optional[GameStage]:
        return self._right_stage

    @right_stage.setter
    def right_stage(self, stage: GameStage):
        self._right_stage = stage
        if not stage.left_stage:
            stage.left_stage = self
            stage.coordinates[0] = self._right_stage.coordinates[0] + 1

    @property
    def left_stage(self) -> Optional[GameStage]:
        return self._left_stage

    @left_stage.setter
    def left_stage(self, stage: GameStage):
        self._left_stage = stage
        if not stage.right_stage:
            stage.right_stage = self
            stage.coordinates[0] = self._left_stage.coordinates[0] - 1

    def set_font(self) -> pygame.Surface:
        """Sets font and returns a text surface"""
        font = pygame.font.SysFont("Arial", 40)
        text = self.name + " Koordinaten: " + str(self.coordinates[0]) + ", " + str(self.coordinates[1])
        return font.render(text, True, pygame.color.Color("blue"))

    def draw_page_name(self) -> None:
        """Draws the page name on top of the window"""
        self.font_surface = self.set_font()

        GAME_WINDOW.blit(
            self.font_surface,
            [
                GAME_WINDOW.get_width() / 2 - self.font_surface.get_width() / 2,
                10
            ]
        )


class GameWorld:
    def __init__(self, stages: Tuple[GameStage, ...]):
        self.stages = stages
        self.current_stage = self.stages[0]


class Map:
    CELL_WIDTH = 40
    CELL_HEIGHT = 40
    CELL_BORDER_COLOR = pygame.color.Color("black")
    CELL_BORDER_COLOR_HIGHLIGHT = pygame.color.Color("red")
    START_POSITION = [SCREEN_SIZE[0] / 2 - CELL_WIDTH / 2, SCREEN_SIZE[1] / 2 - CELL_HEIGHT / 2]

    def __init__(self, game_world: GameWorld):
        self.game_world = game_world

    def draw_map(self):
        """draws the map from the game world stages"""
        for stage in self.game_world.stages:
            color = self.CELL_BORDER_COLOR
            if self.game_world.current_stage == stage:
                color = self.CELL_BORDER_COLOR_HIGHLIGHT
            cell_rect = pygame.Rect(
                self.START_POSITION[0] + stage.coordinates[0] * self.CELL_WIDTH,
                self.START_POSITION[1] + stage.coordinates[1] * self.CELL_HEIGHT,
                self.CELL_WIDTH,
                self.CELL_HEIGHT
            )
            pygame.draw.rect(
                GAME_WINDOW,
                color,
                cell_rect,
                1
            )


class Inventory:
    HEADER_TOP_POSITION = 10
    HEADER_SIZE = 40
    TEXT_TOP_POSITION = 200
    LEFT_CONTAINER_TEXT_MARGIN = 200
    RIGHT_CONTAINER_TEXT_MARGIN = 600
    TEST_SIZE = 20
    TEST_PADDING = TEST_SIZE + 10
    TEST_COLOR = "black"
    TEST_SECONDARY_COLOR = "darkgreen"

    def __init__(self, sprite_group: MainCharGroup):
        self.sprite_group = sprite_group
        self.font_surface_header = self.set_font("Inventory", self.HEADER_SIZE)

    def set_font(self, text: str = "Inventory", size: int = 16, color: str = "blue") -> pygame.Surface:
        """Sets font and returns a text surface"""
        font = pygame.font.SysFont("Arial", size)
        text = text
        return font.render(text, True, pygame.color.Color(color))

    def draw_page(self) -> None:
        """Draws the whole page"""
        self.draw_page_name()
        self.draw_items()
        self.draw_current_item()

    def draw_page_name(self) -> None:
        """Draws the page name on top of the window"""
        GAME_WINDOW.blit(
            self.font_surface_header,
            [
                GAME_WINDOW.get_width() / 2 - self.font_surface_header.get_width() / 2,
                self.HEADER_TOP_POSITION
            ]
        )

    def draw_items(self) -> None:
        """Draws Items of the main char"""
        items = self.sprite_group.sprite.data.items
        top_position = self.TEXT_TOP_POSITION

        GAME_WINDOW.blit(self.set_font(
            "Items:", self.TEST_SIZE, self.TEST_SECONDARY_COLOR), [self.LEFT_CONTAINER_TEXT_MARGIN, top_position])
        top_position = top_position + self.TEST_PADDING
        for item in items:
            item_text_font_surface = self.set_font(item.name, self.TEST_SIZE, self.TEST_COLOR)
            GAME_WINDOW.blit(item_text_font_surface, [200, top_position])
            top_position = top_position + self.TEST_SIZE

    def draw_current_item(self) -> None:
        """Draws Current item of the main char"""
        current_item = self.sprite_group.sprite.data.mainchar.current_item
        top_position = self.TEXT_TOP_POSITION

        GAME_WINDOW.blit(self.set_font(
            "Current Item:",
            self.TEST_SIZE,
            self.TEST_SECONDARY_COLOR),
            [self.RIGHT_CONTAINER_TEXT_MARGIN, top_position]
        )
        top_position = top_position + self.TEST_PADDING
        GAME_WINDOW.blit(self.set_font(
            current_item.name, self.TEST_SIZE, self.TEST_COLOR), [self.RIGHT_CONTAINER_TEXT_MARGIN, top_position])


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

        self._walk_direction = WalkDirection.NONE
        self.movement_type = MovementType.WALK
        self.image_flipped = False
        self.data = load_data()

    @property
    def walk_direction(self) -> WalkDirection:
        return self._walk_direction

    @walk_direction.setter
    def walk_direction(self, walk_direction: WalkDirection):
        self._walk_direction = walk_direction
        self.flip_image_x()

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
        self.walk_direction = WalkDirection.RIGHT

    def walk_left(self) -> None:
        self.rect.x = self.rect.x - self.get_current_speed()
        self.walk_direction = WalkDirection.LEFT

    def walk_down(self) -> None:
        self.rect.y = self.rect.y + self.get_current_speed()

    def solve_for_walking(self, name: str, game_world: GameWorld) -> None:
        """method to find and execute the right walking method based on input"""
        if self.wall_collision_check(game_world):
            return None
        do = f"walk_{name}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            func()

    def wall_collision_check(self, game_world: GameWorld) -> bool:
        """ if next move will hit a wall, return true """
        speed = self.get_current_speed()

        if self.rect.bottomright[0] + speed > SCREEN_SIZE[0] and pygame.key.get_pressed()[K_d]:
            if game_world.current_stage.right_stage:
                game_world.current_stage = game_world.current_stage.right_stage
                self.rect.x = 0
            return True
        if self.rect.bottomright[1] + speed > SCREEN_SIZE[1] and pygame.key.get_pressed()[K_s]:
            if game_world.current_stage.bottom_stage:
                game_world.current_stage = game_world.current_stage.bottom_stage
                self.rect.y = 0
            return True
        if self.rect.x - speed < 0 and pygame.key.get_pressed()[K_a]:
            if game_world.current_stage.left_stage:
                game_world.current_stage = game_world.current_stage.left_stage
                self.rect.x = SCREEN_SIZE[0] - self.rect.width
            return True
        if self.rect.y - speed < 0 and pygame.key.get_pressed()[K_w]:
            if game_world.current_stage.top_stage:
                game_world.current_stage = game_world.current_stage.top_stage
                self.rect.y = SCREEN_SIZE[1] - self.rect.height
            return True
        return False

    def flip_image_x(self) -> None:
        """Flips the main char image horizontally based on the walk_direction"""
        if self.walk_direction is WalkDirection.LEFT and not self.image_flipped:
            self.image = pygame.transform.flip(self.image, True, False)
            self.image_flipped = True
        if self.walk_direction is WalkDirection.RIGHT and self.image_flipped:
            self.image = pygame.transform.flip(self.image, True, False)
            self.image_flipped = False


class MainCharGroup(pygame.sprite.GroupSingle):
    sprite: MainChar

    def sprites(self) -> List[MainChar]:
        return [self.sprite]


def create_stages() -> Tuple[GameStage, ...]:
    """Creates the stages for the game"""
    main_char_group = create_main_char_group()

    start_stage = GameStage(main_char_group, "Start Level")
    right_stage = GameStage(main_char_group, "Right Level")
    top_stage = GameStage(main_char_group, "Top Level")
    left_stage = GameStage(main_char_group, "Left Level")
    bottom_stage = GameStage(main_char_group, "Bottom Level")

    start_stage.right_stage = right_stage
    start_stage.top_stage = top_stage
    start_stage.left_stage = left_stage
    start_stage.bottom_stage = bottom_stage

    return start_stage, right_stage, top_stage, left_stage, bottom_stage


def create_game_world() -> GameWorld:
    stages = create_stages()

    return GameWorld(stages)


def create_map(game_world: GameWorld) -> Map:
    return Map(game_world)


def create_inventory(sprite_group: MainCharGroup) -> Inventory:
    return Inventory(sprite_group)


def create_main_char() -> MainChar:
    char = MainChar([0, 200])

    return char


def create_main_char_group() -> MainCharGroup:
    char = create_main_char()
    group = MainCharGroup(char)

    return group


def load_data() -> DataModel:
    data_model = DataModel()

    return data_model
