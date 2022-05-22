from enum import Enum, auto

import pygame
from pygame.locals import *

from game_world import MainChar, MovementType, create_game_world, GameWorld
from menu import Menu, create_menu, GAME_WINDOW, GAME_DISPLAY


class GameState(Enum):
    MENU = auto()
    GAME = auto()


class Game:
    def __init__(self, game_state: GameState = GameState.GAME):
        self.game_state = game_state


def toggle_game_state(game: Game) -> None:
    if game.game_state == game.game_state.MENU:
        game.game_state = GameState.GAME
    else:
        game.game_state = GameState.MENU


def handle_game_close_events(event) -> bool:
    """returns false, if the game should be quit on closing window with escape or quit"""
    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        return False
    return True


def handle_pause_event(event, game: Game) -> None:
    if event.type == KEYDOWN and event.key == K_p:
        toggle_game_state(game)


def handle_keyboard_events(game_world: GameWorld) -> None:
    handle_walking(game_world)


def handle_walking(game_world: GameWorld) -> None:
    if pygame.key.get_pressed()[K_LSHIFT]:
        game_world.current_stage.sprite_group.sprite.movement_type = MovementType.SPRINT
    else:
        game_world.current_stage.sprite_group.sprite.movement_type = MovementType.WALK
    [
        game_world.current_stage.sprite_group.sprite.solve_for_walking(MainChar.MAPPED_WALKING[key])
        for key, key_active in enumerate(pygame.key.get_pressed())
        if key_active and key in MainChar.MAPPED_WALKING
    ]


def handle_mouse_events(event, menu: Menu) -> None:
    if event.type == MOUSEBUTTONDOWN:
        for sprite in menu.current_page.button_group:
            if sprite.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                sprite.on_click(menu)


def check_user_action(menu: Menu, game_world: GameWorld, game: Game) -> bool:
    """Check User Action. return false on quit events from user"""
    for event in pygame.event.get():
        handle_pause_event(event, game)
        if not handle_game_close_events(event):
            return False
        handle_mouse_events(event, menu)
    handle_keyboard_events(game_world)

    return True


def loop(menu: Menu, game_world: GameWorld) -> None:
    """Running the pygame loop. set different stuff for window each loop"""
    game = Game()

    while True:
        # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
        if not check_user_action(menu, game_world, game):
            pygame.quit()
            break

        # Spiellogik

        # Spielfeld löschen
        GAME_WINDOW.fill(pygame.color.Color("grey"))

        # Spielfeld/figuren zeichnen
        if game.game_state == GameState.MENU:
            menu.current_page.button_group.draw(GAME_WINDOW)
            menu.current_page.button_group.update(surface=GAME_WINDOW)
            menu.current_page.draw_page_name()
        if game.game_state == GameState.GAME:
            game_world.current_stage.sprite_group.draw(GAME_WINDOW)

        # Fenster aktualisieren
        GAME_DISPLAY.flip()
        clock = pygame.time.Clock()
        clock.tick(60)


def main() -> None:
    pygame.init()
    pygame.mixer.init()

    menu = create_menu()
    game_world = create_game_world()

    loop(menu, game_world)


if __name__ == '__main__':
    main()
