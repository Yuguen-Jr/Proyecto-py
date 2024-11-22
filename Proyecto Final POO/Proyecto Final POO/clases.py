
class Jugador:
    vida = 100
    daño = 10
    size = 180
    
    
    def __init__(self,puerto_local, nombre):
        self.nombre = nombre
        self.id = puerto_local
    
    def recibir_daño(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0:
            print(f"{self.nombre} ha muerto")
        else:
            print(f"{self.nombre} recibió {cantidad} de daño. Vida restante: {self.vida}")
    
    def curarse(self, cantidad):
        self.vida += cantidad
        print(f"{self.nombre} se curó {cantidad}. Vida actual: {self.vida}")


class Obstaculo:
    def __init__(self, tipo, posicion):
        self.tipo = tipo
        self.posicion = posicion

    def __repr__(self):
        return f"Obstáculo({self.tipo}) en {self.posicion}"


class ObjetoCuracion:
    def __init__(self, cantidad, posicion):
        self.cantidad = cantidad
        self.posicion = posicion
    
    def usar(self, personaje):
        personaje.curarse(self.cantidad)
        print(f"{personaje.nombre} ha recogido un objeto de curación en la posición {self.posicion}")


class Mapa:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.obstaculos = []
        self.objetos_curacion = []

    def agregar_obstaculo(self, obstaculo):
        self.obstaculos.append(obstaculo)
    
    def agregar_objeto_curacion(self, objeto):
        self.objetos_curacion.append(objeto)
    
    def mostrar_mapa(self):
        print(f"Mapa de {self.ancho}x{self.alto}")
        for obstaculo in self.obstaculos:
            print(obstaculo)
        for objeto in self.objetos_curacion:
            print(f"Objeto de curación en {objeto.posicion}, que cura {objeto.cantidad}")



