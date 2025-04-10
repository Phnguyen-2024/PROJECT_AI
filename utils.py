import pygame
pygame.init()

def load_image(filepath, tile_size):
    image = pygame.image.load(filepath)
    return pygame.transform.scale(image, (tile_size, tile_size))