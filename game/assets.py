import pygame

def load_and_scale_fruit(path, tile_size):
    raw = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(raw, (int(tile_size * 0.8), int(tile_size * 0.8)))
    return raw, img