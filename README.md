# Sistema de Roteamento Logístico (VRP Paralelo)

Aplicação desenvolvida em Python para otimização de rotas logísticas. O sistema utiliza algoritmos de grafos para minimizar a distância total percorrida por uma frota heterogênea, suportando entregas parciais (Split Delivery).

## Algoritmos Implementados

1.  **Floyd-Warshall ($O(V^3)$):**
    * Calcula a matriz de caminhos mínimos entre todos os pontos do mapa.
    * Garante que os veículos sempre utilizem o menor trajeto possível entre dois nós.

2.  **Roteamento Paralelo Guloso (Global Greedy):**
    * Move toda a frota simultaneamente.
    * A cada passo, o algoritmo avalia **todas as combinações possíveis** entre (Veículos Disponíveis) e (Clientes com Demanda).
    * O movimento escolhido é sempre aquele que adiciona o menor custo (distância) ao sistema naquele momento.
    * Isso garante uma minimização mais eficiente do custo total da operação.

3.  **Entrega Parcial (Split Delivery):**
    * Se um cliente precisa de 100 itens e o caminhão só tem espaço para 40, o sistema realiza a entrega de 40 e mantém os 60 restantes pendentes para outro veículo.

## Estrutura

sistema_de_roteamento/  
├── src/  
│   ├── logic.py      # Lógica Paralela e Floyd-Warshall  
│   ├── models.py     # Classes Location e Vehicle  
│   ├── interface.py  # Interface Tkinter Interativa  
├── main.py           # Executável  
├── README.md  

  
Guilherme Morais Araujo         RA: 251023826  
Lorenzo Camillo de Avila        RA: 241024323  
Viviane Mei Takuno Nakasato     RA: 241020832  