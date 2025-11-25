import tkinter as tk
from tkinter import simpledialog, messagebox
from src.logic import RoutingController

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.controller = RoutingController() # Conecta com a camada lógica
        # Paleta de cores para diferenciar as rotas de cada veículo
        self.colors = ["blue", "green", "orange", "purple", "brown", "magenta", "cyan", "red"]
        self.setup_ui()

    # --------------------------------------------------------------------------
    # Configura todo o layout da janela: Painel esquerdo (inputs) e Canvas (mapa)
    # --------------------------------------------------------------------------
    def setup_ui(self):
        # --- PAINEL ESQUERDO (CONTROLES) ---
        left_frame = tk.Frame(self.root, width=320, bg="#f0f0f0", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="Configuração Logística", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        # 1. Configuração de Demandas (Define o Mapa)
        grp_cenario = tk.LabelFrame(left_frame, text="1. Demandas dos Clientes", bg="#f0f0f0", padx=5, pady=5)
        grp_cenario.pack(fill=tk.X, pady=5)

        tk.Label(grp_cenario, text="Digite as cargas (separadas por vírgula):", bg="#f0f0f0").pack(anchor="w")
        tk.Label(grp_cenario, text="Isso definirá a quantidade de clientes.", font=("Arial", 8), fg="gray", bg="#f0f0f0").pack(anchor="w")
        
        self.ent_demands = tk.Entry(grp_cenario)
        self.ent_demands.insert(0, "10, 20, 15, 50, 30") # Exemplo inicial
        self.ent_demands.pack(fill=tk.X, pady=5)
        
        tk.Button(grp_cenario, text="Gerar Mapa Baseado nas Demandas", command=self.generate_scenario, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=5)

        # 2. Configuração de Frota
        grp_fleet = tk.LabelFrame(left_frame, text="2. Frota (Veículos)", bg="#f0f0f0", padx=5, pady=5)
        grp_fleet.pack(fill=tk.X, pady=5)
        
        tk.Label(grp_fleet, text="Capacidades (separadas por vírgula):", bg="#f0f0f0").pack(anchor="w")
        self.ent_fleet = tk.Entry(grp_fleet)
        self.ent_fleet.insert(0, "50, 50")
        self.ent_fleet.pack(fill=tk.X, pady=5)

        # Botão Principal de Cálculo
        tk.Button(left_frame, text="CALCULAR ROTAS", command=self.calculate, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill=tk.X, pady=20)

        # Área de Log (Relatório textual)
        tk.Label(left_frame, text="Relatório:", bg="#f0f0f0", anchor="w").pack(fill=tk.X)
        self.txt_log = tk.Text(left_frame, height=15, width=30, font=("Consolas", 8))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # --- ÁREA DIREITA (CANVAS DE DESENHO) ---
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Vincula o clique do mouse no canvas à função de edição
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # --------------------------------------------------------------------------
    # Lê a lista de demandas, valida e solicita ao controller a criação dos nós
    # --------------------------------------------------------------------------
    def generate_scenario(self):
        raw_text = self.ent_demands.get()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        # Garante dimensões mínimas caso a janela ainda esteja carregando
        if w < 50: w, h = 800, 600

        try:
            if not raw_text.strip():
                raise ValueError("Caixa vazia")

            # Converte string "10, 20" em lista de inteiros [10, 20]
            demands_list = [int(x.strip()) for x in raw_text.split(",") if x.strip()]
            
            if not demands_list:
                raise ValueError("Lista vazia")

            # Chama o controller para criar os objetos Location
            self.controller.generate_scenario_from_demands(demands_list, w, h)
            
            self.draw_scene()
            self.log(f"Mapa gerado com sucesso!\n{len(demands_list)} clientes criados.\nDepósito posicionado no centro.")
            
        except ValueError:
            messagebox.showerror("Erro de Formatação", "Por favor, insira números inteiros separados por vírgula.\nExemplo: 10, 50, 25")

    # --------------------------------------------------------------------------
    # Lê a configuração da frota e dispara o algoritmo de roteamento paralelo
    # --------------------------------------------------------------------------
    def calculate(self):
        fleet_str = self.ent_fleet.get()
        try:
            # Converte string "50, 50" em lista de capacidades [50, 50]
            caps = [int(x.strip()) for x in fleet_str.split(",") if x.strip()]
            if not caps: raise ValueError
            
            # Chama o algoritmo principal na camada lógica
            vehicles, log_txt = self.controller.solve_multivehicle_vrp(caps)
            
            self.draw_scene(vehicles)
            self.log(log_txt)
        except ValueError:
            messagebox.showerror("Erro", "Formato da frota inválido.\nUse números separados por vírgula.")

    # --------------------------------------------------------------------------
    # Evento de clique no Canvas: Permite editar a demanda de um nó manualmente
    # --------------------------------------------------------------------------
    def on_canvas_click(self, event):
        # Identifica se clicou próximo de algum objeto desenhado
        clicked_item = self.canvas.find_closest(event.x, event.y, halo=5)
        if clicked_item:
            tags = self.canvas.gettags(clicked_item)
            # Verifica se o objeto tem a tag de identificação 'node_ID'
            node_tag = next((t for t in tags if t.startswith("node_")), None)
            
            if node_tag:
                node_id = int(node_tag.split("_")[1])
                if node_id == 0: return # Ignora clique no depósito
                
                # Abre popup para digitar novo valor
                new_dem = simpledialog.askinteger("Editar", f"Nova demanda para Cliente {node_id}:", minvalue=0, maxvalue=1000)
                if new_dem is not None:
                    self.controller.update_demand(node_id, new_dem)
                    self._update_input_from_model()
                    self.draw_scene()

    # ------------------------------------------------------------------------------
    # Atualiza o campo de texto de input para refletir as mudanças feitas via clique
    # ------------------------------------------------------------------------------
    def _update_input_from_model(self):
        clients = [str(loc.demand) for loc in self.controller.locations if not loc.is_depot]
        self.ent_demands.delete(0, tk.END)
        self.ent_demands.insert(0, ", ".join(clients))

    # ---------------------------------------------------------------------
    # Renderiza visualmente o grafo (nós e arestas) e as rotas dos veículos
    # ---------------------------------------------------------------------
    def draw_scene(self, vehicles=None):
        self.canvas.delete("all")
        locs = self.controller.locations

        # 1. Desenha os Nós (Locais)
        for loc in locs:
            color = "#D32F2F" if loc.is_depot else "#388E3C"
            r = 18
            tag_id = f"node_{loc.id}"
            
            # Círculo
            self.canvas.create_oval(loc.x-r, loc.y-r, loc.x+r, loc.y+r, fill=color, outline="black", tags=tag_id)
            
            # Texto do ID
            lbl = "D" if loc.is_depot else str(loc.id)
            self.canvas.create_text(loc.x, loc.y, text=lbl, fill="white", font=("Arial", 10, "bold"), tags=tag_id)
            
            # Texto da Demanda (acima do nó)
            if not loc.is_depot:
                self.canvas.create_text(loc.x, loc.y-25, text=f"Q:{loc.demand}", font=("Arial", 9, "bold"), fill="#333")

        # 2. Desenha as Rotas (se existirem)
        if vehicles:
            offset_step = 3 # Distância para separar linhas sobrepostas
            
            for i, veh in enumerate(vehicles):
                if len(veh.route) < 2: continue
                
                # Seleciona cor baseada no índice do veículo
                c_idx = i % len(self.colors)
                route_color = self.colors[c_idx]
                
                # Calcula deslocamento visual para evitar sobreposição
                offset = (i * offset_step) - (len(vehicles) * offset_step / 2)
                
                for j in range(len(veh.route) - 1):
                    u = next(l for l in locs if l.id == veh.route[j])
                    v = next(l for l in locs if l.id == veh.route[j+1])
                    
                    self.canvas.create_line(u.x + offset, u.y + offset, 
                                          v.x + offset, v.y + offset, 
                                          fill=route_color, width=2, arrow=tk.LAST)

    # -----------------------------------------------
    # Helper para escrever mensagens no painel de log
    # -----------------------------------------------
    def log(self, text):
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.insert(tk.END, text)