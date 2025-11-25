import tkinter as tk
from src.interface import MainWindow

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sistema Logístico Multi-Veículo (Floyd-Warshall)")
    
    # Define o tamanho inicial da janela
    root.geometry("1000x650")
    
    # Instancia a classe principal da Interface, passando a raiz do Tkinter
    app = MainWindow(root)
    
    # Inicia o loop de eventos (mantém a janela aberta)
    root.mainloop()