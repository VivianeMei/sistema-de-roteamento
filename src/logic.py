import math
import random
from src.models import Location, Vehicle

class RoutingController:
    def __init__(self):
        self.locations = [] # Guarda os objetos Location
        self.vehicles = []  # Guarda os objetos Vehicle
        self.dist_matrix = []   # Guarda a distância entre cada par de pontos
        self.fw_dist_matrix = []    # Guarda o caminho mínimo entre todos os pares

    #----------------------------------------------------------------------------------
    # Cria um cenário, com os clientes em coordenadas aleatórias e o depósito no centro
    #----------------------------------------------------------------------------------
    def generate_scenario_from_demands(self, demands_list, width, height):
        self.locations = []
        
        # 1. Depósito (Centro)
        self.locations.append(Location(0, width//2, height//2, demand=0, is_depot=True))
        
        # 2. Clientes
        for i, demand_value in enumerate(demands_list):
            client_id = i + 1
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            self.locations.append(Location(client_id, x, y, demand=demand_value))

        self._calculate_distances()
        return len(self.locations)


    # -------------------------------------------
    # Atualiza a demanda de um cliente específico
    # -------------------------------------------
    def update_demand(self, node_id, new_demand):
        for loc in self.locations:
            if loc.id == node_id and not loc.is_depot:
                loc.demand = new_demand
                break

    # ---------------------------------------------------------------------------------------------
    # Calcula a distância física (em linha reta) de todos para todos e monta a matriz de adjacência
    # ---------------------------------------------------------------------------------------------
    def _calculate_distances(self):
        n = len(self.locations)
        self.dist_matrix = [[float('inf')] * n for _ in range(n)]
        
        for i in range(n):
            self.dist_matrix[i][i] = 0
            for j in range(n):
                if i != j:
                    l1 = self.locations[i]
                    l2 = self.locations[j]
                    dist = math.sqrt((l1.x - l2.x)**2 + (l1.y - l2.y)**2)
                    self.dist_matrix[i][j] = dist

    # ---------------------------------------------------------------------------------------------
    # Algoritmo de Floyd-Warshall calcula os caminhos mínimos de todas as lojas para todas as lojas
    # ---------------------------------------------------------------------------------------------
    def run_floyd_warshall(self):
        # Algoritmo de caminhos mínimos O(V^3)
        n = len(self.locations)
        dist = [row[:] for row in self.dist_matrix]
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        self.fw_dist_matrix = dist


    # --------------------------------------------------------------------------
    # A frota de caminhões trabalha em conjunto para minimizar a distância total
    # --------------------------------------------------------------------------
    def solve_multivehicle_vrp(self, vehicle_capacities):
        
        # Roteamento Paralelo Guloso (Parallel Nearest Neighbor).
        # Otimiza a distância TOTAL da frota.
        
        if not self.locations:
            return [], "Cenário vazio! Gere o mapa primeiro."

        self.run_floyd_warshall()

        # Inicializa Frota
        self.vehicles = []
        for idx, cap in enumerate(vehicle_capacities):
            v = Vehicle(idx + 1, cap)
            v.route = [0] # Todos começam no depósito
            self.vehicles.append(v)

        # Controle de Demandas Pendentes
        pending_demands = {loc.id: loc.demand for loc in self.locations if not loc.is_depot}
        
        logs = []
        logs.append("--- Iniciando Otimização Global (Paralela) ---")
        
        step_count = 0
        
        while True:
            # Verifica se ainda há demanda
            total_pending = sum(pending_demands.values())
            if total_pending <= 0:
                break
                
            # Verifica se a frota inteira está cheia
            all_full = True
            for v in self.vehicles:
                if v.load < v.capacity:
                    all_full = False
                    break
            if all_full:
                logs.append("Frota totalmente cheia. Encerrando entregas.")
                break

            # Procuramos qual é o MELHOR movimento entre TODOS os veículos e TODOS os clientes
            best_dist = float('inf')
            best_vehicle = None
            best_client_id = None
            
            for veh in self.vehicles:
                # Se o veículo já está cheio, ignora ele
                if veh.load >= veh.capacity:
                    continue
                
                current_node = veh.route[-1]
                
                for client_id, amount in pending_demands.items():
                    if amount > 0:
                        # Distância via Floyd-Warshall
                        d = self.fw_dist_matrix[current_node][client_id]
                        
                        # Se achou uma distância menor que a melhor registrada até agora, salva
                        if d < best_dist:
                            best_dist = d
                            best_vehicle = veh
                            best_client_id = client_id

            # Se encontrou um movimento válido
            if best_vehicle and best_client_id is not None:
                # Realiza a entrega (parcial ou total)
                space = best_vehicle.capacity - best_vehicle.load
                needed = pending_demands[best_client_id]
                deliver = min(space, needed)
                
                # Atualiza o Veículo
                best_vehicle.route.append(best_client_id)
                best_vehicle.load += deliver
                best_vehicle.travel_cost += best_dist
                
                # Atualiza a demanda pendente
                pending_demands[best_client_id] -= deliver
                
                logs.append(f"Passo {step_count}: Veículo {best_vehicle.id} foi ao Cliente {best_client_id}. Entregou {deliver}.")
                step_count += 1
            else:
                # Não achou caminho 
                break

        # Retorna todos os veículos ao depósito
        logs.append("--- Fim das Demandas ou Capacidade ---")
        total_fleet_dist = 0
        
        for veh in self.vehicles:
            last_node = veh.route[-1]
            dist_home = self.fw_dist_matrix[last_node][0]
            
            if dist_home > 0:
                veh.route.append(0)
                veh.travel_cost += dist_home
                logs.append(f"Veículo {veh.id} retornou ao depósito (+{dist_home:.1f}). Total: {veh.travel_cost:.1f}")
            
            total_fleet_dist += veh.travel_cost

        # Resumo final
        logs.append(f"\nDISTÂNCIA TOTAL DA FROTA: {total_fleet_dist:.2f}")
        
        # Checagem de sobras
        remaining = sum(pending_demands.values())
        if remaining > 0:
            logs.append(f"ALERTA: Faltaram entregar {remaining} itens.")

        return self.vehicles, "\n".join(logs)