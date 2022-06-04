from abc import ABC, abstractmethod
from typing import Dict, Callable

import pygame

from mixer import load_menu_background_music, add_music_volume, sub_music_volume, play_sound, BASS_HIT

pygame.font.init()
SCREEN_SIZE = [1300, 900]
GAME_DISPLAY = pygame.display
GAME_DISPLAY.set_caption("GenericRpgV2")
GAME_WINDOW = GAME_DISPLAY.set_mode(SCREEN_SIZE)


class MenuPage:
    def __init__(
            self,
            button_group: pygame.sprite.Group,
            sprite_group: pygame.sprite.Group,
            name: str = "Seite"
    ):
        self.button_group = button_group
        self.sprite_group = sprite_group
        self.name = name
        self.font_surface = self.set_font()

    def set_font(self) -> pygame.Surface:
        """Sets font and returns a text surface"""
        font = pygame.font.SysFont("Arial", 40)
        return font.render(self.name, True, pygame.color.Color("blue"))

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


class Menu:
    def __init__(self, pages: Dict[str, MenuPage]):
        self.pages = pages
        self.current_page = self.pages['page1']


class MenuButton(ABC, pygame.sprite.Sprite):
    # Add later methods as @abstractmethod to text abstract class
    # COLORS
    TEXT_COLOR = "white"

    # SIZES
    BUTTON_SIZE = [200, 80]

    # COLORS
    MENU_BUTTON_COLOR = "palegreen4"
    MENU_BUTTON_FOCUS_COLOR = "palegreen3"

    # pages
    SWITCH_CURRENT_PAGE = None
    SWITCH_TARGET_PAGE = None

    def __init__(self, pos: list, size=None, text="", color: str = pygame.color.Color(MENU_BUTTON_COLOR)):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self._focus = False  # when mouse click down holding
        self.text = text
        self.font_surface = self.set_font(text)
        self.pos = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        if size is None:
            size = self.BUTTON_SIZE
        self.size = size
        self.width = size[0]
        self.height = size[1]
        self.color = color

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.set_image()

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.set_rect()

    @property
    def focus(self) -> bool:
        return self._focus

    @focus.setter
    def focus(self, focus: bool):
        self._focus = focus
        if focus:
            self.image.fill(self.MENU_BUTTON_FOCUS_COLOR)
        else:
            self.image.fill(self.MENU_BUTTON_COLOR)
        self.draw_text()

    def set_font(self, text) -> pygame.Surface:
        """Sets font and returns a text surface"""

        font = pygame.font.SysFont("Arial", 24)
        return font.render(text, True, self.TEXT_COLOR)

    def set_image(self) -> None:
        """Create an button image and blit text over it"""

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.color)
        self.draw_text()

    def draw_text(self) -> None:
        self.image.blit(
            self.font_surface,
            [
                self.width / 2 - self.font_surface.get_width() / 2,
                self.height / 2 - self.font_surface.get_height() / 2
            ]
        )

    def set_rect(self) -> None:
        """Sets the rect and position of an image"""

        self.rect = self.image.get_rect()
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y

    @abstractmethod
    def on_click(self, *args, **kwargs):
        pass

    @staticmethod
    def switch_page(current_page: MenuPage, target_page: MenuPage):
        current_page.active = False
        target_page.active = True


class ProgressBar(ABC, pygame.sprite.Sprite):
    """Layout for a basic Progress Bar"""
    # SIZES
    OUTER_SIZE = [200, 30]

    # COLORS
    OUTER_COLOR = pygame.color.Color("black")
    INNER_COLOR = pygame.color.Color("red")
    TEXT_COLOR = pygame.color.Color("black")

    # FONT
    FONT = pygame.font.SysFont("Arial", 24)

    def __init__(self, pos: list, outer_size=None):
        if outer_size is None:
            outer_size = self.OUTER_SIZE
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([0, 0])
        self.outer_size = outer_size
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def calculate_inner_bar_width(self, percent: int) -> int:
        """A function that calculates the progress width"""
        return int(percent * self.outer_size[0] / 100)

    @abstractmethod
    def calculate_inner_bar_percent(self) -> int:
        """A function that calculates the progress in percent"""
        pass

    def update(self, **kwargs):
        value_percent = self.calculate_inner_bar_percent()
        value_text = str(value_percent) + "%"
        font_surface = self.FONT.render(value_text, True, self.TEXT_COLOR)

        progress_bar_outer_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.outer_size[0],
            self.outer_size[1]
        )
        progress_bar_inner_rect = pygame.Rect(
            self.rect.x + 1,
            self.rect.y + 1,
            self.calculate_inner_bar_width(value_percent),
            self.outer_size[1] - 1
        )
        pygame.draw.rect(
            kwargs.get('surface'),
            self.OUTER_COLOR,
            progress_bar_outer_rect,
            2
        )
        pygame.draw.rect(
            kwargs.get('surface'),
            self.INNER_COLOR,
            progress_bar_inner_rect
        )
        kwargs.get('surface').blit(
            font_surface,
            [
                progress_bar_outer_rect.centerx - font_surface.get_width() / 2,
                progress_bar_outer_rect.centery - font_surface.get_height() / 2,
            ]
        )


class SoundProgressBar(ProgressBar):
    def __init__(self, pos: list, outer_size=None):
        super().__init__(pos, outer_size)

    def calculate_inner_bar_percent(self) -> int:
        """A function that calculates the progress width"""
        bar_width_percent = int(pygame.mixer.music.get_volume() * 100)
        return bar_width_percent


class ActionButton(MenuButton):
    def __init__(self, pos: list, action: Callable, size=None, text="",
                 color: str = pygame.color.Color(MenuButton.MENU_BUTTON_COLOR)):
        MenuButton.__init__(self, pos, size, text, color)
        self.action = action

    def on_click(self, *args, **kwargs):
        # play_sound(BASS_HIT)
        self.action()

    @staticmethod
    def no_action():
        pass


class SwitchButton(MenuButton):
    def __init__(self, target_page: MenuPage, pos: list, size=None, text="Link",
                 color: str = pygame.color.Color(MenuButton.MENU_BUTTON_COLOR)):
        MenuButton.__init__(self, pos, size, text, color)
        self.target_page = target_page

    def on_click(self, menu: Menu):
        if menu.current_page.name is not self.target_page.name:
            menu.current_page = self.target_page


def create_menu_pages() -> Dict[str, MenuPage]:
    menu_page1_sprite_group = pygame.sprite.Group()
    menu_page1_sprite_group.add(
        SoundProgressBar([SCREEN_SIZE[0] / 2 - ActionButton.BUTTON_SIZE[0] / 2, 300])

    )
    menu_page1_button_group = pygame.sprite.Group()
    menu_page1_button_group.add(
        ActionButton(
            [SCREEN_SIZE[0] / 2 - ActionButton.BUTTON_SIZE[0] / 2, 200],
            add_music_volume,
            MenuButton.BUTTON_SIZE,
            "+"
        ),
        ActionButton(
            [SCREEN_SIZE[0] / 2 - ActionButton.BUTTON_SIZE[0] / 2, 400],
            sub_music_volume,
            MenuButton.BUTTON_SIZE,
            "-"
        )
    )
    menu_page1 = MenuPage(
        sprite_group=menu_page1_sprite_group,
        button_group=menu_page1_button_group,
        name="Seite1"
    )

    menu_page2_button_group = pygame.sprite.Group()
    menu_page2_button_group.add(
        ActionButton(
            [SCREEN_SIZE[0] / 2 - ActionButton.BUTTON_SIZE[0] / 2, 200],
            ActionButton.no_action,
            MenuButton.BUTTON_SIZE,
            "Foobar2"
        )
    )
    menu_page2 = MenuPage(
        button_group=menu_page2_button_group,
        sprite_group=pygame.sprite.Group(),
        name="Seite2"
    )

    return {
        "page1": menu_page1,
        "page2": menu_page2
    }


def add_switch_pages(menu_pages: Dict[str, MenuPage]) -> None:
    switch_button = SwitchButton(
        menu_pages['page2'],
        [SCREEN_SIZE[0] / 2 - ActionButton.BUTTON_SIZE[0] / 2, 600]
    )
    switch_button2 = SwitchButton(
        menu_pages['page1'],
        [SCREEN_SIZE[0] / 2 - ActionButton.BUTTON_SIZE[0] / 2, 400]
    )
    menu_pages['page1'].button_group.add(switch_button)
    menu_pages['page2'].button_group.add(switch_button2)


def create_menu() -> Menu:
    menu_pages = create_menu_pages()
    add_switch_pages(menu_pages)
    menu = Menu(menu_pages)
    load_menu_background_music()

    return menu
