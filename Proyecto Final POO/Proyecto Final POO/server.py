import random
import socket
import threading
import math
import json
import time

# Variables globales para manejar los jugadores y proyectiles
players = {}
projectiles = []
clients = [] # Lista de clientes conectados
lock = threading.Lock()  # Evita que varios hilos accedan a la vez a los datos compartidos

# Constantes del servidor
HOST = '127.0.0.1'
PORT = 8000

def clean_up_player(player_id):
    global players, projectiles
    with lock:
        if player_id in players:
            del players[player_id]
        
        # Eliminar proyectiles asociados a ese jugador
        projectiles = [p for p in projectiles if p["owner"] != player_id]

def handle_new_player(player_id, message):
    global players
    with lock:
        if player_id not in players:
            players[player_id] = {
                "x": random.randint(0, 500),
                "y": random.randint(0, 500),
                "angle": random.randint(0, 360),
                "is_alive": True,
                "name": message.get("name", f"Player_{player_id}")
            }
            print(f"Nuevo jugador conectado: {players[player_id]}")

def update_player_position(player_id, message):
    global players
    with lock:
        if player_id in players:
            players[player_id]["x"] = message["x"]
            players[player_id]["y"] = message["y"]
            players[player_id]["angle"] = message["angle"]

def add_projectile(player_id, message):
    global projectiles
    with lock:
        projectiles.append({
            "x": message["x"],
            "y": message["y"],
            "angle": message["angle"],
            "owner": player_id,
            "max_distance": 600,  # Distancia máxima del proyectil
            "traveled_distance": 0
        })

def get_game_state():
    global players, projectiles
    with lock:
        return {
            "players": players,
            "projectiles": projectiles
        }

def clean_up_player(player_id):
    global players, projectiles
    with lock:
        if player_id in players:
            del players[player_id]
        # Eliminar proyectiles asociados al jugador
        # projectiles = [p for p in projectiles if p["owner"] != player_id]

# Manejar la conexión de un cliente
def handle_client(client_socket, addr):
    global projectiles, players
    player_id = str(addr[1])  # Usa el puerto del cliente como un ID único
    clients.append(client_socket)  # Agregar el cliente a la lista de clientes

    while True:
        try:
            # Recibir mensaje del cliente
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break

            # Procesar datos del cliente
            message = json.loads(data)
            
            if message["type"] == "new_player":
                handle_new_player(player_id, message)
            elif message["type"] == "position":
                update_player_position(player_id, message)
            elif message["type"] == "shot":
                add_projectile(player_id, message)
            
            # Enviar el estado del juego al cliente
            game_state = get_game_state()
            #client_socket.sendall(json.dumps(game_state).encode("utf-8"))

            # Enviar el estado del juego a todos los clientes conectados
            for client in clients:
                try:
                    client.sendall(json.dumps(game_state).encode("utf-8"))
                except:
                    print(f"Error al enviar datos al cliente {client}.")

            # Vaciar la lista de proyectiles después de enviar el estado
            with lock:
                projectiles = []
        except Exception as e:
            print(f"Error en la conexión con {addr}: {e}")
            break
        finally:
            # Limpieza al desconectar
            clean_up_player(player_id)
            client_socket.close()
            print(f"Conexión cerrada con {addr}")
    
# Bucle principal del servidor
def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

# Iniciar servidor y bucle de juego
if __name__ == "__main__":
    run_server()
