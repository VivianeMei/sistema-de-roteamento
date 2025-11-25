# Clientes e depósito
class Location:
    def __init__(self, id, x, y, demand=0, is_depot=False):
        self.id = id
        self.x = x  # Coordenadas
        self.y = y
        self.demand = demand    # Demanda
        self.is_depot = is_depot  

# Caminhões
class Vehicle:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity    # Capacidade máxima de carga
        self.load = 0      # Quanto está carregando
        self.route = []     # Lista com os locais visitados
        self.travel_cost = 0    # Distância percorrida