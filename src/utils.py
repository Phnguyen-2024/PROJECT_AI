import pygame
pygame.init()


def load_image(filepath, tile_size):
    image = pygame.image.load(filepath)
    return pygame.transform.scale(image, (tile_size, tile_size))

# Hàm tải icon với kích thước tùy chỉnh
def load_icon(filepath, size):
    icon = pygame.image.load(filepath)
    return pygame.transform.scale(icon, (size, size))