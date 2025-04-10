import random

TILE_TYPES = ["G", "D", "T", "W"]  # Grass, Dirt, Tree, Water

def generate_random_map(rows, cols):
    return [[random.choice(TILE_TYPES) for _ in range(cols)] for _ in range(rows)]