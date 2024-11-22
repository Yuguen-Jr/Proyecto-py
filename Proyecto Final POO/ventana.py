import pygame
import math
import os
from clases import Jugador
# Inicializar Pygame
pygame.init()
def play():
    # Obtener el nombre del jugador
    nombre = input("Ingresa nombre: ")
    Jugador1 = Jugador(1,nombre)

    # Configuración de la pantalla
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("TerraPlane")
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)

    # Cargar imagen de fondo
    background_image = pygame.image.load('fondo_nuevo.jpg')

    background_image = pygame.transform.scale(background_image, (screen_width * 3, screen_height * 3))


    # Obtener dimensiones de la imagen de fondo
    background_width = background_image.get_width()
    background_height = background_image.get_height()

    # Posición inicial del avión (centrado en la pantalla)
    arrow_x = screen_width // 2
    arrow_y = screen_height // 2

    # Velocidades
    player_speed = 25  # Velocidad del avión
    bullet_speed = 25  # Velocidad de las balas

    # Inicializar offset (desplazamiento del fondo)
    offset_x = 0
    offset_y = 0

    frames = []
    frame_count = 0
    frame_duration = 10
    current_frame = 0

    frame_directory = "Movimiento"
    new_frame_size = (Jugador1.size, Jugador1.size)

    # Cargar los cuadros de animación del avión
    for filename in sorted(os.listdir(frame_directory)):
        if filename.endswith('.gif'):
            frame = pygame.image.load(os.path.join(frame_directory, filename))
            resized_frame = pygame.transform.scale(frame, new_frame_size)
            frames.append(resized_frame)

    print(f"Se han cargado {len(frames)} cuadros.")

    # Clase para los proyectiles (balas)
    class Projectile:
        def __init__(self, x, y, angle, max_distance=500):  # Agregamos una distancia máxima de 500 píxeles
            self.map_x = x  # Posición en el mapa, no en la pantalla
            self.map_y = y  # Posición en el mapa, no en la pantalla
            self.angle = angle
            self.speed = bullet_speed
            self.start_x = x
            self.start_y = y
            self.max_distance = max_distance  # Distancia máxima que viajará el proyectil
            self.traveled_distance = 0  # Distancia recorrida hasta ahora

        def update(self):
            # Actualiza la posición del proyectil en el mapa
            self.map_x += self.speed * math.cos(self.angle)
            self.map_y += self.speed * math.sin(self.angle)
            self.traveled_distance = math.sqrt((self.map_x - self.start_x)**2 + (self.map_y - self.start_y)**2)
            
            # Eliminar el proyectil si ha viajado más allá de la distancia máxima
            if self.traveled_distance >= self.max_distance:
                projectiles.remove(self)

        def draw(self, surface, offset_x, offset_y):
            # Dibujar el proyectil en la pantalla ajustando el offset del mapa
            screen_x = self.map_x - offset_x
            screen_y = self.map_y - offset_y
            pygame.draw.circle(surface, WHITE, (int(screen_x), int(screen_y)), 5)


    projectiles = []

    # Inicializar el bucle del juego
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Disparar con el botón del ratón
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Botón izquierdo
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - arrow_x
                dy = mouse_y - arrow_y
                angle = math.atan2(dy, dx)

                # Calcular la posición en el mapa donde se disparó el proyectil
                projectile_x = arrow_x + offset_x + 60 * math.cos(angle)
                projectile_y = arrow_y + offset_y + 60 * math.sin(angle)
                projectiles.append(Projectile(projectile_x, projectile_y, angle))


        safety_margin = 100
        # Movimiento del avión
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            arrow_x -= player_speed
            if arrow_x < safety_margin:
                arrow_x = safety_margin
                offset_x = max(0, offset_x - player_speed)  # Mover el fondo a la izquierda

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            arrow_x += player_speed
            if arrow_x > screen_width - safety_margin:
                arrow_x = screen_width - safety_margin
                offset_x = min(background_width - screen_width, offset_x + player_speed)  # Mover el fondo a la derecha

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            arrow_y -= player_speed
            if arrow_y < safety_margin:
                arrow_y = safety_margin
                offset_y = max(0, offset_y - player_speed)  # Mover el fondo hacia arriba

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            arrow_y += player_speed
            if arrow_y > screen_height - safety_margin:
                arrow_y = screen_height - safety_margin
                offset_y = min(background_height - screen_height, offset_y + player_speed)  # Mover el fondo hacia abajo

        # Dibujar el fondo desplazado
        screen.blit(background_image, (-offset_x, -offset_y))

        # Rotar el avión hacia el puntero del ratón
        if len(frames) > 0:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - arrow_x
            dy = mouse_y - arrow_y
            angle = math.atan2(dy, dx)

            current_image = frames[current_frame]
            rotated_image = pygame.transform.rotate(current_image, -math.degrees(angle))
            rotated_rect = rotated_image.get_rect(center=(arrow_x, arrow_y))
            screen.blit(rotated_image, rotated_rect.topleft)

        # Actualizar y dibujar los proyectiles (balas)
        for projectile in projectiles:
            projectile.update()
            projectile.draw(screen, offset_x, offset_y)  # Ajustar el dibujo de los proyectiles al offset del mapa

        # Dibujar el mini mapa
        mini_map_width = 200
        mini_map_height = 200
        mini_map_rect = pygame.Rect(20, screen_height - mini_map_height - 20, mini_map_width, mini_map_height)
        
        # Dibujar el rectángulo del mini mapa
        pygame.draw.rect(screen, BLACK, mini_map_rect, 2)
        

        # Dibujar el fondo del mini mapa
        mini_map_scale_x = mini_map_width / background_width
        mini_map_scale_y = mini_map_height / background_height

        mini_map_background = pygame.transform.scale(background_image, (int(background_width * mini_map_scale_x), int(background_height * mini_map_scale_y)))
        screen.blit(mini_map_background, mini_map_rect.topleft)

        # Calcular la posición del avión en el mini mapa de manera proporcional
        mini_map_arrow_x = ((arrow_x + offset_x) / background_width) * mini_map_width + mini_map_rect.x
        mini_map_arrow_y = ((arrow_y + offset_y) / background_height) * mini_map_height + mini_map_rect.y

        # Limitar la posición del punto verde dentro del rectángulo del minimapa
        mini_map_arrow_x = max(mini_map_rect.x, min(mini_map_arrow_x, mini_map_rect.right))
        mini_map_arrow_y = max(mini_map_rect.y, min(mini_map_arrow_y, mini_map_rect.bottom))

        # Dibujar la posición del avión en el mini mapa
        pygame.draw.circle(screen, GREEN, (int(mini_map_arrow_x), int(mini_map_arrow_y)), 5)

        pygame.display.flip()


    pygame.quit()
play()