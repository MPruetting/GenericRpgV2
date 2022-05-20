from pathlib import Path

import pygame


# PATHS
MUSIC_PATH = Path.cwd() / 'resources' / 'music'
SOUND_PATH = Path.cwd() / 'resources' / 'sound'


def load_menu_background_music() -> None:
    """ loads background music for the menu"""
    pygame.mixer.music.load(MUSIC_PATH / 'ambience_safe_7dl.ogg')
    set_initial_music_volume()
    pygame.mixer.music.play()


def set_initial_music_volume() -> None:
    pygame.mixer.music.set_volume(0.10)


def add_music_volume() -> None:
    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.1)


def sub_music_volume() -> None:
    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.1)
