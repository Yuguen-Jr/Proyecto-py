import pygame
import socket
import math
import os
import threading  # Maneja la recepción de datos del servidor en paralelo al juego.
import json
from clases import Jugador
last_traveled_distance = 0 
players_lock = threading.Lock()

projectiles = []
projectiles_local= []

players = {}

frame_index = 0 # Contador de cuadros para la animación
last_shot_time = 0  # Tiempo del último disparo
shoot_cooldown = 500

# Variables y constantes del juego
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
screen_width, screen_height = 1280, 720 # Configuración de la pantalla
screen_pos_x = screen_width // 2 # Posición inicial del avión (centrado en la pantalla)
screen_pos_y = screen_height // 2
player_speed = 25  # Velocidad del avión
bullet_speed = 25  # Velocidad de las balas
angle = 0  # Dirección del disparo en radianes.
screen_pos_x1= screen_width // 2
screen_pos_y1= screen_width // 2

offset_x = offset_y = 0 # Inicializar offset (desplazamiento del fondo)

frames = []
frame_count = 0
frame_duration = 5
current_frame = 0

frame_directory = "Movimiento"
new_frame_size = (0, 0)

HOST, PORT = '192.168.137.58' , 5555

# Inicialización del socket del cliente - Conectar al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Obtener el puerto asignado por el SO
ip_local, puerto_local = client_socket.getsockname()
print(f"Puerto local asignado: {puerto_local}")

# Configuración de la pantalla
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("TerraPlane Multijugador")
background_image = pygame.image.load('fondo_nuevo.jpg')
background_image = pygame.transform.scale(background_image, (screen_width * 2, screen_height * 2))
background_width, background_height = background_image.get_width(), background_image.get_height()

# Obtener el nombre del jugador y cargar animación
nombre = input("Ingresa nombre: ")
Jugador1 = Jugador(puerto_local, nombre)

# Función para enviar datos al servidor
def send_to_server(data):
    client_socket.sendall(json.dumps(data).encode("utf-8"))

# Renderizar jugadores remotos

# Actualizar información de jugadores remotos
def update_remote_players(server_data):
    global players
    with players_lock: # Garantiza que un solo hilo acceda a players a la vez
        for player_id, player_data in server_data.items():
            if str(player_id) == str(Jugador1.id):  # Ignora datos del jugador local
                continue
            if player_id not in players:
                players[player_id] = Jugador(player_data["id"], player_data["name"])
            players[player_id].x = player_data["x"]
            players[player_id].y = player_data["y"]
            players[player_id].angle = player_data["angle"]
            print(player_id)

# Actualizar proyectiles con datos del servidor
def update_projectiles(server_projectiles):
    global projectiles
    new_projectiles = []
    for proj in server_projectiles:
        new_projectiles.append(Projectile(proj["x"], proj["y"], proj["angle"], proj["max_distance"]))
    projectiles = new_projectiles

# Función para recibir actualizaciones del servidor

# Inicializar el juego
def initialize_game():
    load_frames()

# Función para manejar los eventos de entrada

class Projectile:
    def __init__(self, x, y, angle, max_distance=600):  # Agregamos una distancia máxima de 500 píxeles
        self.map_x, self.map_y = x, y  # Posición en el mapa, no en la pantalla
        self.angle = angle
        self.speed = bullet_speed
        self.start_x, self.start_y = x, y
        self.max_distance = max_distance  # Distancia máxima que viajará el proyectil
        self.traveled_distance = 0
        self.distance=0# Distancia recorrida hasta ahora

    def update(self):   # Calcula la nueva posición del proyectil según su velocidad y ángulo. Si supera la distancia máxima, se elimina del juego
        # Actualiza la posición del proyectil en el mapa
        self.map_x += self.speed * math.cos(self.angle)
        self.map_y += self.speed * math.sin(self.angle)
        self.traveled_distance = math.sqrt((self.map_x - self.start_x)**2 + (self.map_y - self.start_y)**2)
        self.distance=self.traveled_distance
        # Eliminar el proyectil si ha viajado más allá de la distancia máxima
        if self.traveled_distance >= self.max_distance:
            if self in projectiles:
                projectiles.remove(self)
    
    def get_distance(self):
        self.map_x += self.speed * math.cos(self.angle)
        self.map_y += self.speed * math.sin(self.angle)
        self.traveled_distance = math.sqrt((self.map_x - self.start_x)**2 + (self.map_y - self.start_y)**2)
        self.distance=self.traveled_distance
        return self.distance
            
    def draw(self, surface, offset_x, offset_y): 
        # Dibuja el proyectil en la pantalla ajustando el desplazamiento (offset_x, offset_y) del mapa.
        screen_x = self.map_x - offset_x
        screen_y = self.map_y - offset_y
        pygame.draw.circle(surface, WHITE, (int(screen_x), int(screen_y)), 5)

def receive_data_from_server():
    while True:
        try:
            data = client_socket.recv(4096)
            if data:
                game_state = json.loads(data.decode("utf-8"))
                
                # Actualizar el estado del juego con la información del servidor
                if "players" in game_state:
                    update_remote_players(game_state.get("players", {}))
                if "projectiles" in game_state:
                    update_projectiles(game_state.get("projectiles", []))
        except Exception as e:
            print("Error recibiendo datos del servidor:", e)
            break

def handle_events():
    global projectiles, offset_x, offset_y, last_shot_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            current_time = pygame.time.get_ticks()  # Tiempo actual en milisegundos
            if current_time - last_shot_time >= shoot_cooldown:
                create_projectile(event)
                last_shot_time = current_time  # Actualizamos el tiempo del último disparo
    return True

# Crear proyectil
def create_projectile(event):
    global projectiles, projectiles_local, last_traveled_distance
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx, dy = mouse_x - screen_pos_x, mouse_y - screen_pos_y
    angle = math.atan2(dy, dx)
    # Calcular la posición en el mapa donde se disparó el proyectil
    projectile_x = screen_pos_x + offset_x + 60 * math.cos(angle)
    projectile_y = screen_pos_y + offset_y + 60 * math.sin(angle)
    projectiles_local.append(Projectile(projectile_x, projectile_y, angle))
    send_to_server({"type": "shot", "x": projectile_x, "y": projectile_y,"owner": Jugador1.id, "angle": angle,})

#send_to_server({"type": "shot", "x": 0,"y": 0,"owner": "","angle": 0,"traveled_distance": 0})

def update_players():
    global offset_x, offset_y
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_player(-player_speed, 0)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_player(player_speed, 0)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        move_player(0, -player_speed)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move_player(0, player_speed)

def move_player(player_speed_dx, player_speed_dy):
    global screen_pos_x, screen_pos_y, offset_x, offset_y
    safety_margin = 100
    screen_pos_x += player_speed_dx
    screen_pos_y += player_speed_dy
    
    if screen_pos_x < safety_margin:
        screen_pos_x = safety_margin
        offset_x = max(0, offset_x - player_speed)
    if screen_pos_x > screen_width - safety_margin:
        screen_pos_x = screen_width - safety_margin
        offset_x = min(background_width - screen_width, offset_x + player_speed)
    if screen_pos_y < safety_margin:
        screen_pos_y = safety_margin
        offset_y = max(0, offset_y - player_speed)
    if screen_pos_y > screen_height - safety_margin:
        screen_pos_y = screen_height - safety_margin
        offset_y = min(background_height - screen_height, offset_y + player_speed)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx, dy = mouse_x - screen_pos_x, mouse_y - screen_pos_y
    angle = math.atan2(dy, dx)
    send_to_server({"type": "position", "x": screen_pos_x, "y": screen_pos_y, "angle": angle})

# Función para Dibujar el mini mapa
def mini_map():
    # Muestra la posición relativa del jugador en un mapa reducido
    mini_map_width, mini_map_height = 200, 200
    #mini_map_rect = pygame.Rect(20, screen_height - mini_map_height - 20, mini_map_width, mini_map_height)

    mini_map_rect = pygame.Rect(20, screen_height - mini_map_height - 20, mini_map_width, mini_map_height)
    
    # Dibujar el rectángulo del mini mapa
    pygame.draw.rect(screen, BLACK, mini_map_rect, 2)

    # Dibujar el fondo del mini mapa
    mini_map_scale_x = mini_map_width / background_width
    mini_map_scale_y = mini_map_height / background_height

    mini_map_background = pygame.transform.scale(background_image, (int(background_width * mini_map_scale_x), int(background_height * mini_map_scale_y)))
    screen.blit(mini_map_background, mini_map_rect.topleft)
    #pygame.draw.circle(screen, GREEN, (int(mini_map_arrow_x), int(mini_map_arrow_y)), 5)
    mini_map_screen_pos_x = ((screen_pos_x + offset_x) / background_width) * mini_map_width + mini_map_rect.x
    mini_map_screen_pos_y = ((screen_pos_y + offset_y) / background_height) * mini_map_height + mini_map_rect.y

    # Limitar la posición del punto verde dentro del rectángulo del minimapa
    mini_map_screen_pos_x = max(mini_map_rect.x, min(mini_map_screen_pos_x, mini_map_rect.right))
    mini_map_screen_pos_y = max(mini_map_rect.y, min(mini_map_screen_pos_y, mini_map_rect.bottom))

    # Dibujar la posición del avión en el mini mapa
    pygame.draw.circle(screen, GREEN, (int(mini_map_screen_pos_x), int(mini_map_screen_pos_y)), 5)

def draw_remote_players():
    global players, frames, frame_index
    with players_lock: #Bloquear el acceso durante la lectura
        for player_id, player in players.items():
            if str(player_id) != str(Jugador1.id):
                player_screen_x = player.x
                player_screen_y = player.y
                rotated_image = pygame.transform.rotate(frames[frame_index], -math.degrees(player.angle))
                rotated_rect = rotated_image.get_rect(center=(player_screen_x, player_screen_y))
                screen.blit(rotated_image, rotated_rect.topleft)
                print(player_screen_x,player_screen_y,player.angle)

# Renderizar todos los elementos
def render():
    global frames, frame_index

    # Dibujar el fondo desplazado. 
    # # Si el jugador se acerca a los bordes de la pantalla, el fondo se desplaza para simular un mapa más grande.
    screen.blit(background_image, (-offset_x, -offset_y))

    if frames:
        # Actualizar el índice del cuadro 
        frame_index = (frame_index + 1) % len(frames)  # Ciclar a través de frames[]

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - screen_pos_x, mouse_y - screen_pos_y
        angle = math.atan2(dy, dx)
        
        # Rotar el primer cuadro de animación según el ángulo hacia el mouse
        rotated_image = pygame.transform.rotate(frames[frame_index], -math.degrees(angle))
        rotated_rect = rotated_image.get_rect(center=(screen_pos_x, screen_pos_y))
        
        # Dibujar el avión rotado en la pantalla
        screen.blit(rotated_image, rotated_rect.topleft)
    
    draw_remote_players()
    
    # Actualizar y dibujar los proyectiles (balas)
    for projectile in projectiles:
        projectile.update()
        projectile.draw(screen, offset_x, offset_y)  # Ajustar el dibujo de los proyectiles al offset del mapa
    
    mini_map()

# Función para cargar los cuadros de animación del avión desde el directorio Movimiento y los redimensiona para ajustarse al tamaño del jugador.
def load_frames():
    global frames
    new_frame_size = (Jugador1.size, Jugador1.size)
    for filename in sorted(os.listdir(frame_directory)):
        if filename.endswith('.gif'):
            frame = pygame.image.load(os.path.join(frame_directory, filename))
            resized_frame = pygame.transform.scale(frame, new_frame_size)
            frames.append(resized_frame)
    print(f"Se han cargado {len(frames)} cuadros.")

def load_image(frame_file):
    # Cargar la imagen desde la carpeta raíz
    frame = pygame.image.load(frame_file)
    # Redimensionar la imagen si es necesario
    resized_frame = pygame.transform.scale(frame, (Jugador1.size, Jugador1.size))
    return resized_frame
frame_file= "frame-1.gif"
frame_image= load_image(frame_file)

# Función principal del juego
def main():
    initialize_game()
    send_to_server({"type": "new_player", "name": Jugador1.nombre})
    # Iniciar hilo para recibir datos del servidor
    receive_thread = threading.Thread(target=receive_data_from_server, daemon=True)
    receive_thread.start()
    
    running = True
    while running:
        running = handle_events()
        update_players()
        render()
        draw_remote_players()
        pygame.display.flip()
    pygame.quit()
    client_socket.close()

if __name__ == "__main__":
    main()
