import pygame

class Player:
    def __init__(self, screen, sprite, start_pos=(0, 0), tile_size=64):
        self.screen = screen
        self.sprite = pygame.transform.scale(sprite, (tile_size, tile_size))  # Kích thước nhân vật bằng kích thước ô
        self.row, self.col = start_pos  # Vị trí ban đầu (hàng, cột)
        self.tile_size = tile_size

    def move(self, direction, rows, cols, tilemap):
        # Di chuyển theo hướng Đông, Tây, Nam, Bắc
        if direction == "UP" and self.row > 0 and tilemap[self.row - 1][self.col] != "T":
            self.row -= 1
        elif direction == "DOWN" and self.row < rows - 1 and tilemap[self.row + 1][self.col] != "T":
            self.row += 1
        elif direction == "LEFT" and self.col > 0 and tilemap[self.row][self.col - 1] != "T":
            self.col -= 1
        elif direction == "RIGHT" and self.col < cols - 1 and tilemap[self.row][self.col + 1] != "T":
            self.col += 1

    def render(self):
        # Vẽ nhân vật tại vị trí hiện tại
        x = self.col * self.tile_size
        y = self.row * self.tile_size
        self.screen.blit(self.sprite, (x, y))