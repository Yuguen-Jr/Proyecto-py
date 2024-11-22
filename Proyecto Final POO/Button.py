import pygame

class Buttons:
    def __init__(self, image_path, hover_image_path, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.hover_image = pygame.image.load(hover_image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.hover_image = pygame.transform.scale(self.hover_image, (width, height))

    def draw(self, surface, mouse_pos):
        # Cambiar la imagen si el mouse está sobre el botón
        if self.is_clicked(mouse_pos):
            surface.blit(self.hover_image, self.rect.topleft)
        else:
            surface.blit(self.image, self.rect.topleft)

    def is_clicked(self, pos):
        # Comprobar si el botón fue clickeado o si el mouse esta encima del boton
        return self.rect.collidepoint(pos)
