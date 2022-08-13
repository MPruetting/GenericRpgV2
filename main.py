from enum import Enum, auto

import pygame
from pygame.locals import *

from debug import Debug
from game_world import MainChar, MovementType, create_game_world, GameWorld, create_map, Map, load_data
from menu import Menu, create_menu, GAME_WINDOW, GAME_DISPLAY, GAME_CLOCK


class GameState(Enum):
    MENU = auto()
    GAME = auto()
    MAP = auto()


class Game:
    def __init__(self, game_state: GameState = GameState.GAME):
        self.game_state = game_state
        self.game_state_events = {
            GameState.GAME: [
                handle_pause_event,
                handle_map_event
            ],
            GameState.MAP: [
                handle_pause_event,
                handle_map_event
            ],
            GameState.MENU: [
                menu_click_events,
                handle_pause_event
            ]
        }
        self.data = load_data()


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


def handle_keyboard_events(game_world: GameWorld, game: Game) -> None:
    if game.game_state == GameState.GAME:
        handle_walking(game_world)


def handle_walking(game_world: GameWorld) -> None:
    if pygame.key.get_pressed()[K_LSHIFT]:
        game_world.current_stage.sprite_group.sprite.movement_type = MovementType.SPRINT
    else:
        game_world.current_stage.sprite_group.sprite.movement_type = MovementType.WALK
    [
        game_world.current_stage.sprite_group.sprite.solve_for_walking(MainChar.MAPPED_WALKING[key], game_world)
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


def check_user_action(menu: Menu, game_world: GameWorld, game: Game) -> bool:
    """Check User Action. return false on quit events from user"""
    for event in pygame.event.get():
        for event_function in game.game_state_events[game.game_state]:
            event_function(event, game, menu)
        if not handle_game_close_events(event):
            return False
    handle_keyboard_events(game_world, game)
    return True


def draw_sprites(menu: Menu, game_world: GameWorld, game_map: Map, game: Game) -> None:
    """Draws the sprites for the game, map, pause menu, etc"""
    if game.game_state == GameState.MENU:
        menu.current_page.button_group.draw(GAME_WINDOW)
        menu.current_page.sprite_group.draw(GAME_WINDOW)
        menu.current_page.sprite_group.update(surface=GAME_WINDOW)
        menu.current_page.draw_page_name()
    if game.game_state == GameState.GAME:
        game_world.current_stage.sprite_group.draw(GAME_WINDOW)
        game_world.current_stage.draw_page_name()
    if game.game_state == GameState.MAP:
        game_map.draw_map()


def loop(menu: Menu, game_world: GameWorld, game_map: Map, debug: Debug) -> None:
    """Running the pygame loop. set different stuff for window each loop"""
    game = Game()
    mainchar = game_world.current_stage.sprite_group.sprite
    mainchar.data = game.data.mainchar

    while True:
        # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
        if not check_user_action(menu, game_world, game):
            pygame.quit()
            break

        # Spiellogik

        # Spielfeld löschen
        GAME_WINDOW.fill(pygame.color.Color("grey"))

        # Spielfeld/figuren zeichnen
        draw_sprites(menu, game_world, game_map, game)
        debug.display_debug_output(
            [
                {"name": "Game State", "text": game.game_state},
                {"name": "Main Char Stats", "text": mainchar.data}
            ]
        )

        # Fenster aktualisieren
        GAME_DISPLAY.flip()
        GAME_CLOCK.tick(60)


def main() -> None:
    pygame.init()

    menu = create_menu()
    game_world = create_game_world()
    game_map = create_map(game_world)
    debug = Debug(screen=GAME_WINDOW)

    loop(menu, game_world, game_map, debug)


if __name__ == '__main__':
    main()
