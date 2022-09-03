from enum import Enum, auto
from typing import NamedTuple

import pygame
from pygame.locals import *

from debug import Debug
from game_world import MainChar, MovementType, create_game_world, GameWorld, create_map, Map
from inventory import Inventory, create_inventory
from menu import Menu, create_menu, GAME_WINDOW, GAME_DISPLAY, GAME_CLOCK


class GameState(Enum):
    MENU = auto()
    GAME = auto()
    MAP = auto()
    Inventory = auto()


class Game:
    def __init__(self, game_state: GameState = GameState.GAME):
        self.game_state = game_state
        self.game_state_events = {
            GameState.GAME: [
                handle_pause_event,
                handle_map_event,
                handle_inventory_event
            ],
            GameState.MAP: [
                handle_pause_event,
                handle_map_event,
                handle_inventory_event
            ],
            GameState.MENU: [
                menu_click_events,
                handle_pause_event
            ],
            GameState.Inventory: [
                handle_pause_event,
                handle_map_event,
                handle_inventory_event
            ],
        }


class GameComponents(NamedTuple):
    game: Game
    game_world: GameWorld
    map: Map
    menu: Menu
    debug: Debug
    inventory: Inventory


def menu_click_events(event, game: Game, menu: Menu):
    handle_mouse_events(event, menu)


def set_game_state(game: Game, new_state: GameState) -> None:
    if game.game_state == new_state:
        game.game_state = GameState.GAME
    else:
        game.game_state = new_state


def handle_game_close_events(event) -> bool:
    """returns false, if the game should be quit on closing window with escape or quit"""
    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        return False
    return True


def handle_pause_event(event, game: Game, menu: Menu) -> None:
    if event.type == KEYDOWN and event.key == K_p:
        set_game_state(game, GameState.MENU)


def handle_map_event(event, game: Game, menu: Menu) -> None:
    if event.type == KEYDOWN and event.key == K_m:
        set_game_state(game, GameState.MAP)


def handle_inventory_event(event, game: Game, menu: Menu) -> None:
    if event.type == KEYDOWN and event.key == K_i:
        set_game_state(game, GameState.Inventory)


def handle_keyboard_events(game_world: GameWorld, game: Game) -> None:
    if game.game_state == GameState.GAME:
        handle_walking(game_world)


def handle_walking(game_world: GameWorld) -> None:
    main_sprite = game_world.current_stage.sprite_group.sprite
    if pygame.key.get_pressed()[K_LSHIFT]:
        main_sprite.movement_type = MovementType.SPRINT
    else:
        main_sprite.movement_type = MovementType.WALK
    [
        main_sprite.solve_for_walking(MainChar.MAPPED_WALKING[key], game_world)
        for key, key_active in enumerate(pygame.key.get_pressed())
        if key_active and key in MainChar.MAPPED_WALKING
    ]


def handle_mouse_events(event, menu: Menu) -> None:
    if event.type == MOUSEBUTTONDOWN:
        for button in menu.current_page.button_group:
            if button.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                button.focus = True
    if event.type == MOUSEBUTTONUP:
        for button in menu.current_page.button_group:
            if button.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) and button.focus:
                button.on_click(menu)
            button.focus = False


def check_user_action(game_components: GameComponents) -> bool:
    """Check User Action. return false on quit events from user"""
    for event in pygame.event.get():
        for event_function in game_components.game.game_state_events[game_components.game.game_state]:
            event_function(event, game_components.game, game_components.menu)
        if not handle_game_close_events(event):
            return False
    handle_keyboard_events(game_components.game_world, game_components.game)
    return True


def draw_sprites(game_components: GameComponents) -> None:
    """Draws the sprites for the game, map, pause menu, etc"""
    if game_components.game.game_state == GameState.MENU:
        game_components.menu.current_page.button_group.draw(GAME_WINDOW)
        game_components.menu.current_page.sprite_group.draw(GAME_WINDOW)
        game_components.menu.current_page.sprite_group.update(surface=GAME_WINDOW)
        game_components.menu.current_page.draw_page_name()

    if game_components.game.game_state == GameState.GAME:
        game_components.game_world.current_stage.sprite_group.draw(GAME_WINDOW)
        game_components.game_world.current_stage.draw_page_name()

    if game_components.game.game_state == GameState.MAP:
        game_components.map.draw_map()

    if game_components.game.game_state == GameState.Inventory:
        game_components.inventory.current_item_fonts.draw(GAME_WINDOW)
        game_components.inventory.all_item_fonts.draw(GAME_WINDOW)
        game_components.inventory.draw_page_name()


def loop(game_components: GameComponents) -> None:
    """Running the pygame loop. set different stuff for window each loop"""
    while True:
        # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
        if not check_user_action(game_components):
            pygame.quit()
            break

        # Spiellogik

        # Spielfeld löschen
        GAME_WINDOW.fill(pygame.color.Color("grey"))

        # Spielfeld/figuren zeichnen
        draw_sprites(game_components)
        # game_components.debug.display_debug_output(
        #     [
        #         {"name": "Game State", "text": game_components.game.game_state},
        #         {"name": "Main Char Stats", "text": mainchar.data}
        #     ]
        # )

        # Fenster aktualisieren
        GAME_DISPLAY.flip()
        GAME_CLOCK.tick(60)


def main() -> None:
    pygame.init()

    game_world = create_game_world()
    game_map = create_map(game_world)
    inventory = create_inventory(game_world.current_stage.sprite_group.sprite.data)

    game_components = GameComponents(
        Game(),
        game_world,
        game_map,
        create_menu(),
        Debug(screen=GAME_WINDOW),
        inventory
    )
    loop(game_components)


if __name__ == '__main__':
    main()
