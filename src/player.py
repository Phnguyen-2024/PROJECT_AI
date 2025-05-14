import pygame

class Player:
    def __init__(self, screen, sprite, start_pos=(0, 0), tile_size=64):
        self.screen = screen
        self.sprite = pygame.transform.scale(sprite, (tile_size, tile_size))
        self.row, self.col = start_pos
        self.tile_size = tile_size
        self.PANEL_TOP_HEIGHT = 100

    def move(self, direction, rows, cols, tilemap):
        new_row, new_col = self.row, self.col
        if direction == "UP" and self.row > 0 and tilemap[self.row - 1][self.col] != "T":
            new_row -= 1
        elif direction == "DOWN" and self.row < rows - 1 and tilemap[self.row + 1][self.col] != "T":
            new_row += 1
        elif direction == "LEFT" and self.col > 0 and tilemap[self.row][self.col - 1] != "T":
            new_col -= 1
        elif direction == "RIGHT" and self.col < cols - 1 and tilemap[self.row][self.col + 1] != "T":
            new_col += 1
        
        if (new_row, new_col) != (self.row, self.col):
            self.row, self.col = new_row, new_col
            return True
        return False

    def render(self):
        x = self.col * self.tile_size
        y = self.row * self.tile_size + self.PANEL_TOP_HEIGHT
        self.screen.blit(self.sprite, (x, y))
