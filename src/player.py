import pygame

class Player:
    def __init__(self, screen, sprite, start_pos=(0, 0), tile_size=64):
        self.screen = screen
        self.sprite = pygame.transform.scale(sprite, (tile_size, tile_size))
        self.row, self.col = start_pos
        self.tile_size = tile_size

    def move(self, direction, rows, cols, tilemap):
        prev_row, prev_col = self.row, self.col

        if direction == "UP" and self.row > 0:
            if tilemap[self.row - 1][self.col] != "T":
                self.row -= 1
        elif direction == "DOWN" and self.row < rows - 1:
            if tilemap[self.row + 1][self.col] != "T":
                self.row += 1
        elif direction == "LEFT" and self.col > 0:
            if tilemap[self.row][self.col - 1] != "T":
                self.col -= 1
        elif direction == "RIGHT" and self.col < cols - 1:
            if tilemap[self.row][self.col + 1] != "T":
                self.col += 1

        return (self.row, self.col) != (prev_row, prev_col)

    def render(self):
        x = self.col * self.tile_size
        y = self.row * self.tile_size
        self.screen.blit(self.sprite, (x, y))