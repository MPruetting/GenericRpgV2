from typing import List

import pygame

from menu import GAME_WINDOW
from models import DataModel


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

    def __init__(self, current_item_fonts: pygame.sprite.Group, all_item_fonts: pygame.sprite.Group):
        self.current_item_fonts = current_item_fonts
        self.all_item_fonts = all_item_fonts
        self.font_surface_header = set_font("Inventory", self.HEADER_SIZE)
        print(self.all_item_fonts, all_item_fonts)

    def draw_page_name(self) -> None:
        """Draws the page name on top of the window"""
        GAME_WINDOW.blit(
            self.font_surface_header,
            [
                GAME_WINDOW.get_width() / 2 - self.font_surface_header.get_width() / 2,
                self.HEADER_TOP_POSITION
            ]
        )


class InventoryText(pygame.sprite.Sprite):
    """Class for drawing Header and normal text in the Inventory"""

    def __init__(self, font: pygame.Surface, pos: List[int]):
        pygame.sprite.Sprite.__init__(self)

        self.image = font
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]
        self.rect.top = pos[1]


def set_font(text: str = "Inventory", size: int = 16, color: str = "blue") -> pygame.Surface:
    """Sets font and returns a text surface"""
    font = pygame.font.SysFont("Arial", size)
    text = text
    return font.render(text, True, pygame.color.Color(color))


def create_inventory_item_fonts(data: DataModel) -> List[InventoryText]:
    items = data.items
    top_position = Inventory.TEXT_TOP_POSITION
    fonts = [InventoryText(
        set_font(
            "Items:",
            Inventory.TEST_SIZE,
            Inventory.TEST_SECONDARY_COLOR
        ),
        [Inventory.LEFT_CONTAINER_TEXT_MARGIN, top_position]
    )]
    top_position = top_position + Inventory.TEST_PADDING
    for item in items:
        item_text_font_surface = set_font(item.name, Inventory.TEST_SIZE, Inventory.TEST_COLOR)
        fonts.append(InventoryText(
            item_text_font_surface,
            [200, top_position])
        )
        top_position = top_position + Inventory.TEST_SIZE

    return fonts


def create_inventory_current_item_fonts(data: DataModel) -> List[InventoryText]:
    current_item = data.mainchar.current_item
    top_position = Inventory.TEXT_TOP_POSITION
    fonts = [InventoryText(
        set_font(
            "Current Item:",
            Inventory.TEST_SIZE,
            Inventory.TEST_SECONDARY_COLOR),
        [Inventory.RIGHT_CONTAINER_TEXT_MARGIN, top_position]
    )]
    top_position = top_position + Inventory.TEST_PADDING
    fonts.append(InventoryText(
        set_font(
            current_item.name,
            Inventory.TEST_SIZE,
            Inventory.TEST_COLOR
        ),
        [Inventory.RIGHT_CONTAINER_TEXT_MARGIN, top_position]
    ))

    return fonts


def create_inventory(data: DataModel) -> Inventory:
    all_item_inventory_font_group = pygame.sprite.Group()
    current_item_inventory_font_group = pygame.sprite.Group()

    all_item_inventory_font_group.add(create_inventory_item_fonts(data))
    current_item_inventory_font_group.add(create_inventory_current_item_fonts(data))

    return Inventory(current_item_inventory_font_group, all_item_inventory_font_group)
