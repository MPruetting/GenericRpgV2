import pygame

from menu import GAME_CLOCK


class Draw:
    """
     Hauptprogramm zum Verwalten von Zeichnungen

    ## Arguments
    - `screen`, ein `screen` objekt von pygame
    """

    # COLORS
    BLACK = (0, 0, 0)

    def __init__(self, screen):
        self.screen = screen

    def draw_font(self, text, size, pos, color=(0, 0, 0),
                  font_fam="Arial", bold=False, ita=False, anti_ali=True):
        """
        Zeichnet einen `text` Text in Größe von `size`, Farbe `color`
        (Liste mit RGB-Werten) und der Familie `font_fam`
        mit Position `pos` auf dem Surface `screen`.

        Zusätzlich kann man den Text bold `bold` oder italic `ita` machen.
        Anti-Aliasing `anti_ali` für den Text, kann man deaktivieren.
        """
        font = pygame.font.SysFont(font_fam, size, bold, ita)
        text_render = font.render(text, anti_ali, color)

        self.screen.blit(text_render, pos)

    def draw_forms(self, color, pos):
        """
        Zeichnet Formen im Spiel auf das Fenster (`screen`).
        (Momentan nur Vierecken)
        - `color`: Farbe des Textes (list)
        - `pos`: eine Liste von x und y Positionen
        und Breite und Höhe zum Positionieren im `screen`
        """
        pygame.draw.rect(self.screen, color, pos, 1)


class Debug:
    """
     Debugausgaben-Programm für pygam

    ## Arguments
    - `screen`, ein `screen` objekt von pygame
    """

    # GAME
    FONT_SIZE = 20

    def __init__(self, screen):
        self.screen = screen
        self.draw = Draw(screen)

    def display_test_text(self, pos):
        """ Gibt einen Test-Text aus oben im Screen, indem es `font` und `text`
        -Objekte initialisiert
        """
        self.draw.draw_font("Test", 30, pos)

    def display_debug_output(self):
        """ Gibt Debug ausgaben über pygame aus"""
        text_rows = [
            f"FPS: {GAME_CLOCK.get_fps()}",
            f"Fenstergroese: {self.screen.get_size()}",
            f"Mausposition: {pygame.mouse.get_pos()}",
        ]
        height_pos = self.FONT_SIZE
        for row in text_rows:
            self.draw.draw_font(row, self.FONT_SIZE, [20, height_pos])
            height_pos += self.FONT_SIZE + 5
