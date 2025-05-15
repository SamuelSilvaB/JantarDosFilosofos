import threading
import time
import tkinter as tk
import math
from random import randint

# Configurações
NUM_FILOSOFOS = 5
TEMPO_PENSANDO = (1, 3) 
TEMPO_COMENDO = (1, 3)   

class Estado:
    PENSANDO = "pensando"
    FOME = "com_fome"
    COMENDO = "comendo"

class Filosofo(threading.Thread):
    def __init__(self, id, garfo_esquerda, garfo_direita, semaforo, gui):
        super().__init__()
        self.id = id
        self.garfo_esquerda = garfo_esquerda
        self.garfo_direita = garfo_direita
        self.semaforo = semaforo
        self.estado = Estado.PENSANDO
        self.gui = gui
        self.executando = True

    def pegar_garfos(self):
        # para previnir o deadlock eu pensei em fazer filosofos pares e impares pegar os garfos em ordem doferentes
        if self.id % 2 == 0:
            first, second = self.garfo_esquerda, self.garfo_direita
        else:
            first, second = self.garfo_direita, self.garfo_esquerda

        self.estado = Estado.FOME
        self.gui.atualizar_estado(self.id, self.estado)

        first.acquire()
        second.acquire()

    def soltar_garfos(self):
        self.garfo_esquerda.release()
        self.garfo_direita.release()

    def run(self):
        while self.executando:
            # Pensando
            self.estado = Estado.PENSANDO
            self.gui.atualizar_estado(self.id, self.estado)
            time.sleep(randint(*TEMPO_PENSANDO))

            # Tentando comer
            with self.semaforo:
                self.pegar_garfos()
                
                # Comendo
                self.estado = Estado.COMENDO
                self.gui.atualizar_estado(self.id, self.estado)
                time.sleep(randint(*TEMPO_COMENDO))
                
                self.soltar_garfos()

class JantarFilosofosGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jantar dos Filósofos")
        
        # Cores para os estados
        self.cores = {
            Estado.PENSANDO: "blue",
            Estado.FOME: "red",
            Estado.COMENDO: "green"
        }
        
        # tela para desenho
        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack(expand=True, fill='both')
        
        # Posições dos filósofos
        self.posicoes = self.calcular_posicoes()
        
        # Desenho inicial
        self.desenhar_mesa()
        self.filosofos_circles = self.desenhar_filosofos()
        
    def calcular_posicoes(self):
        posicoes = []
        centro_x, centro_y = 200, 200
        raio = 150
        for i in range(NUM_FILOSOFOS):
            angulo = (2 * math.pi * i) / NUM_FILOSOFOS - math.pi/2
            x = centro_x + raio * math.cos(angulo)
            y = centro_y + raio * math.sin(angulo)
            posicoes.append((x, y))
        return posicoes
    
    def desenhar_mesa(self):
        # Mesa
        self.canvas.create_oval(50, 50, 350, 350, fill="lightgray")
        
    def desenhar_filosofos(self):
        circles = []
        for i, (x, y) in enumerate(self.posicoes):
            circle = self.canvas.create_oval(
                x-20, y-20, x+20, y+20,
                fill=self.cores[Estado.PENSANDO],
                tags=f"filosofo_{i}"
            )
            self.canvas.create_text(x, y, text=str(i), fill="white")
            circles.append(circle)
        return circles
    
    def atualizar_estado(self, id_filosofo, estado):
        self.canvas.itemconfig(
            self.filosofos_circles[id_filosofo],
            fill=self.cores[estado]
        )
        self.root.update()

def main():
    root = tk.Tk()
    gui = JantarFilosofosGUI(root)
    
    # Criando recursos compartilhados
    garfos = [threading.Lock() for _ in range(NUM_FILOSOFOS)]
    semaforo = threading.Semaphore(NUM_FILOSOFOS - 1)  # Previne deadlock
    
    # Criando e iniciando filósofos
    filosofos = []
    for i in range(NUM_FILOSOFOS):
        f = Filosofo(
            i,
            garfos[i],
            garfos[(i + 1) % NUM_FILOSOFOS],
            semaforo,
            gui
        )
        filosofos.append(f)
        f.start()
    
    def encerrar():
        for f in filosofos:
            f.executando = False
        root.quit()
    
    root.protocol("WM_DELETE_WINDOW", encerrar)
    root.mainloop()

if __name__ == "__main__":
    main()