import pygame
from pygame.locals import *

from game_world import create_main_char_group, MainCharGroup, MainChar, MovementType
from menu import Menu, create_menu, GAME_WINDOW, GAME_DISPLAY


def handle_keyboard_events(main_char: MainCharGroup) -> bool:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            return False
    handle_walking(main_char)
    return True


def handle_walking(main_char: MainCharGroup) -> None:
    if pygame.key.get_pressed()[K_LSHIFT]:
        main_char.sprite.movement_type = MovementType.SPRINT
    else:
        main_char.sprite.movement_type = MovementType.WALK
    [
        main_char.sprite.solve_for_walking(MainChar.MAPPED_WALKING[key])
        for key, key_active in enumerate(pygame.key.get_pressed())
        if key_active and key in MainChar.MAPPED_WALKING
    ]


def handle_mouse_events(event, menu: Menu) -> None:
    if event.type == MOUSEBUTTONDOWN:
        for sprite in menu.current_page.button_group:
            if sprite.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                sprite.on_click(menu)


def check_user_action(menu: Menu, main_char: MainCharGroup) -> bool:
    """Check User Action. return false on quit events from user"""
    if not handle_keyboard_events(main_char):
        return False
    for event in pygame.event.get():
        handle_mouse_events(event, menu)
    return True


def loop(menu: Menu, main_char: MainCharGroup) -> None:
    """Running the pygame loop. set different stuff for window each loop"""
    while True:
        # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
        if not check_user_action(menu, main_char):
            pygame.quit()
            break

        # Spiellogik

        # Spielfeld löschen
        GAME_WINDOW.fill(pygame.color.Color("grey"))

        # Spielfeld/figuren zeichnen
        menu.current_page.button_group.draw(GAME_WINDOW)
        menu.current_page.button_group.update(surface=GAME_WINDOW)
        menu.current_page.draw_page_name()

        main_char.draw(GAME_WINDOW)

        # Fenster aktualisieren
        GAME_DISPLAY.flip()
        clock = pygame.time.Clock()
        clock.tick(60)


def main() -> None:
    pygame.init()
    pygame.mixer.init()

    menu = create_menu()
    main_char = create_main_char_group()

    loop(menu, main_char)


if __name__ == '__main__':
    main()
