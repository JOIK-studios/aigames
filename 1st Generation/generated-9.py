#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL LABERINTO VIVO
El mapa muta mientras caminas. Aprende de ti. Te odia.
"""

import os
import sys
import time
import random
from collections import deque

# ==================== VISUALES ====================

class C:
    END = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"
    WHITE = "\033[97m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== ALGORITMOS DE LABERINTO ====================

class Maze:
    def __init__(self, width=21, height=11, hostility=1.0):
        # Dimensiones impares para paredes gruesas entre celdas
        self.w = width if width % 2 == 1 else width + 1
        self.h = height if height % 2 == 1 else height + 1
        self.hostility = hostility  # 1.0 a 10.0
        self.grid = [[1 for _ in range(self.w)] for _ in range(self.h)]
        self.visited = set()
        self.generate()
    
    def in_bounds(self, x, y):
        return 0 < x < self.w-1 and 0 < y < self.h-1
    
    def carve(self, x, y):
        self.grid[y][x] = 0
    
    def is_wall(self, x, y):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return True
        return self.grid[y][x] == 1
    
    def generate(self):
        """DFS recursivo con backtracking."""
        self.grid = [[1 for _ in range(self.w)] for _ in range(self.h)]
        stack = [(1, 1)]
        self.carve(1, 1)
        visited = {(1, 1)}
        
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for dx, dy in [(0,-2),(0,2),(-2,0),(2,0)]:
                nx, ny = cx+dx, cy+dy
                if self.in_bounds(nx, ny) and (nx, ny) not in visited:
                    neighbors.append((nx, ny, cx+dx//2, cy+dy//2))
            
            if neighbors:
                nx, ny, wx, wy = random.choice(neighbors)
                self.carve(wx, wy)
                self.carve(nx, ny)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Asegurar que los bordes son paredes sólidas
        for x in range(self.w):
            self.grid[0][x] = 1
            self.grid[self.h-1][x] = 1
        for y in range(self.h):
            self.grid[y][0] = 1
            self.grid[y][self.w-1] = 1
    
    def mutate(self, player_x, player_y, goal_x, goal_y):
        """
        El laberinto cambia. Celdas lejanas al jugador se reconfiguran.
        Hostilidad alta = más cambios, más cerca del jugador.
        """
        changes = int(self.hostility * 3) + random.randint(0, 2)
        safe_radius = max(2, 6 - int(self.hostility))  # Zona segura alrededor del jugador
        
        candidates = []
        for y in range(1, self.h-1):
            for x in range(1, self.w-1):
                dist = abs(x - player_x) + abs(y - player_y)
                if dist > safe_radius:
                    candidates.append((x, y))
        
        random.shuffle(candidates)
        modified = []
        
        for x, y in candidates[:changes]:
            old = self.grid[y][x]
            # No mutar la posición del jugador o meta directamente
            if (x, y) == (player_x, player_y) or (x, y) == (goal_x, goal_y):
                continue
            
            # Invertir estado con probabilidad
            if old == 1:
                # Convertir pared en pasillo (más probable en hostilidad alta)
                if random.random() < 0.4 + (self.hostility * 0.05):
                    self.grid[y][x] = 0
                    modified.append((x, y))
            else:
                # Convertir pasillo en pared (más peligroso)
                if random.random() < 0.2 + (self.hostility * 0.04):
                    self.grid[y][x] = 1
                    modified.append((x, y))
        
        # Verificar conectividad: si jugador quedó atrapado o meta inalcanzable, reparar
        if not self.has_path(player_x, player_y, goal_x, goal_y):
            self.repair_path(player_x, player_y, goal_x, goal_y)
            return True, "¡El laberinto intentó atraparte! Se abrió un corredor de emergencia."
        
        if modified:
            return True, f"El laberinto muta: {len(modified)} celdas alteradas."
        return False, "El silencio... por ahora."
    
    def has_path(self, x1, y1, x2, y2):
        """BFS para verificar conectividad."""
        if self.is_wall(x1, y1) or self.is_wall(x2, y2):
            return False
        q = deque([(x1, y1)])
        seen = {(x1, y1)}
        while q:
            cx, cy = q.popleft()
            if (cx, cy) == (x2, y2):
                return True
            for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                nx, ny = cx+dx, cy+dy
                if self.in_bounds(nx, ny) and (nx, ny) not in seen and not self.is_wall(nx, ny):
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return False
    
    def repair_path(self, x1, y1, x2, y2):
        """Fuerza un camino A* mínimo entre dos puntos."""
        # A* simple
        open_set = [(0, x1, y1)]
        came_from = {}
        g_score = {(x1, y1): 0}
        
        while open_set:
            open_set.sort(key=lambda x: x[0])
            _, cx, cy = open_set.pop(0)
            if (cx, cy) == (x2, y2):
                break
            for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                nx, ny = cx+dx, cy+dy
                if not self.in_bounds(nx, ny):
                    continue
                tentative = g_score.get((cx, cy), 999) + 1
                if tentative < g_score.get((nx, ny), 999):
                    came_from[(nx, ny)] = (cx, cy)
                    g_score[(nx, ny)] = tentative
                    f = tentative + abs(nx-x2) + abs(ny-y2)
                    open_set.append((f, nx, ny))
        
        # Reconstruir y abrir camino
        current = (x2, y2)
        while current in came_from:
            x, y = current
            self.grid[y][x] = 0
            current = came_from[current]
        self.grid[y1][x1] = 0
    
    def find_empty(self, exclude=None):
        """Encuentra celda vacía aleatoria."""
        exclude = exclude or set()
        attempts = 0
        while attempts < 1000:
            x = random.randrange(1, self.w-1, 2)
            y = random.randrange(1, self.h-1, 2)
            if not self.is_wall(x, y) and (x, y) not in exclude:
                return (x, y)
            attempts += 1
        # Fallback
        for y in range(1, self.h-1):
            for x in range(1, self.w-1):
                if not self.is_wall(x, y) and (x, y) not in exclude:
                    return (x, y)
        return (1, 1)

# ==================== JUGADOR Y ESTADÍSTICAS ====================

class Player:
    def __init__(self):
        self.x = 1
        self.y = 1
        self.steps = 0
        self.backtracks = 0
        self.start_time = time.time()
        self.trail = deque(maxlen=20)
    
    def reset(self, x, y):
        self.x, self.y = x, y
        self.steps = 0
        self.backtracks = 0
        self.start_time = time.time()
        self.trail.clear()

class AdaptiveAI:
    """Mide tu rendimiento y ajusta la hostilidad del laberinto."""
    def __init__(self):
        self.hostility = 1.0
        self.floor = 1
        self.efficiency_history = []
        self.mutations_count = 0
    
    def calculate_efficiency(self, player, maze, goal_x, goal_y):
        """0-100. 100 = camino perfecto."""
        dist = abs(player.x - goal_x) + abs(player.y - goal_y)
        if player.steps == 0:
            return 100.0
        # Idealmente debería tomar al menos dist pasos
        ideal = max(dist, 1)
        eff = (ideal / player.steps) * 100 if player.steps > 0 else 100
        return min(100, eff)
    
    def adapt(self, player, maze, goal_x, goal_y):
        eff = self.calculate_efficiency(player, maze, goal_x, goal_y)
        self.efficiency_history.append(eff)
        if len(self.efficiency_history) > 5:
            self.efficiency_history.pop(0)
        
        avg_eff = sum(self.efficiency_history) / len(self.efficiency_history)
        
        # Ajuste de hostilidad
        if avg_eff > 75:
            self.hostility = min(10.0, self.hostility + 0.8)
        elif avg_eff > 50:
            self.hostility = min(10.0, self.hostility + 0.3)
        elif avg_eff < 30:
            self.hostility = max(1.0, self.hostility - 0.5)
        
        maze.hostility = self.hostility
        return eff

# ==================== MOTOR DEL JUEGO ====================

class Game:
    def __init__(self):
        self.ai = AdaptiveAI()
        self.maze = Maze(21, 11, self.ai.hostility)
        self.player = Player()
        self.goal = (self.maze.w-2, self.maze.h-2)
        self.messages = []
        self.total_steps_all_floors = 0
        self.place_entities()
    
    def place_entities(self):
        self.player.reset(1, 1)
        self.player.trail.append((1, 1))
        # La meta se mueve ligeramente según hostilidad
        gx, gy = self.maze.find_empty(exclude={(1,1)})
        # Preferir esquina opuesta
        candidates = []
        for y in range(self.maze.h-2, 0, -1):
            for x in range(self.maze.w-2, 0, -1):
                if not self.maze.is_wall(x, y):
                    candidates.append((x, y))
                    if len(candidates) > 5:
                        break
            if len(candidates) > 5:
                break
        if candidates:
            self.goal = random.choice(candidates[:3])
        else:
            self.goal = (gx, gy)
    
    def next_floor(self):
        self.ai.floor += 1
        self.ai.hostility = min(10.0, self.ai.hostility + 0.5)
        
        # Laberinto más grande cada 3 pisos
        new_w = 21 + (self.ai.floor // 3) * 4
        new_h = 11 + (self.ai.floor // 3) * 2
        new_w = min(61, new_w)
        new_h = min(31, new_h)
        
        self.maze = Maze(new_w, new_h, self.ai.hostility)
        self.place_entities()
        self.messages.append(f"{C.GREEN}{C.BOLD}¡Piso {self.ai.floor} alcanzado!{C.END} El laberinto crece.")
    
    def move_player(self, dx, dy):
        nx, ny = self.player.x + dx, self.player.y + dy
        if not self.maze.is_wall(nx, ny):
            # Detectar retroceso
            if len(self.player.trail) >= 2 and (nx, ny) == self.player.trail[-2]:
                self.player.backtracks += 1
            
            self.player.x, self.player.y = nx, ny
            self.player.steps += 1
            self.player.trail.append((nx, ny))
            self.total_steps_all_floors += 1
            
            # MUTACIÓN: cada paso puede desencadenar cambio
            mut_freq = max(1, 5 - int(self.ai.hostility * 0.4))
            if self.player.steps % mut_freq == 0:
                mutated, msg = self.maze.mutate(self.player.x, self.player.y, self.goal[0], self.goal[1])
                if mutated:
                    self.ai.mutations_count += 1
                    self.messages.append(f"{C.YELLOW}{msg}{C.END}")
            
            # Verificar meta
            if (self.player.x, self.player.y) == self.goal:
                self.next_floor()
                return True
        else:
            self.messages.append(f"{C.RED}¡Bump!{C.END}")
        
        # Adaptar dificultad cada 5 pasos
        if self.player.steps % 5 == 0:
            eff = self.ai.adapt(self.player, self.maze, self.goal[0], self.goal[1])
            if eff > 80:
                self.messages.append(f"{C.RED}El laberinto te detecta. Se vuelve agresivo.{C.END}")
            elif eff < 30:
                self.messages.append(f"{C.GREEN}El laberinto te subestima...{C.END}")
        
        return False
    
    def render(self):
        clear()
        mx, my = self.maze.w, self.maze.h
        
        # Marco superior
        print(f"{C.BLUE}{C.BOLD}╔{'═'*(mx+2)}╗{C.END}")
        
        for y in range(my):
            row = [f"{C.BLUE}║{C.END}"]
            for x in range(mx):
                if x == self.player.x and y == self.player.y:
                    row.append(f"{C.CYAN}{C.BOLD}@{C.END}")
                elif (x, y) == self.goal:
                    # Parpadeo de meta
                    sym = '◆' if self.player.steps % 2 == 0 else '◇'
                    row.append(f"{C.GREEN}{C.BOLD}{sym}{C.END}")
                elif (x, y) in self.player.trail and not self.maze.is_wall(x, y):
                    # Rastro
                    row.append(f"{C.DIM}·{C.END}")
                elif self.maze.is_wall(x, y):
                    # Paredes con variación visual según hostilidad
                    if self.ai.hostility > 7:
                        sym = random.choice(['▓', '█', '▒']) if random.random() < 0.1 else '█'
                    else:
                        sym = '█'
                    row.append(f"{C.WHITE}{sym}{C.END}")
                else:
                    row.append(' ')
            row.append(f"{C.BLUE}║{C.END}")
            print(''.join(row))
        
        print(f"{C.BLUE}{C.BOLD}╚{'═'*(mx+2)}╝{C.END}")
        
        # UI
        elapsed = time.time() - self.player.start_time
        eff = self.ai.calculate_efficiency(self.player, self.maze, self.goal[0], self.goal[1])
        
        print(f"\n{C.BOLD}Piso: {C.GREEN}{self.ai.floor}{C.END}  |  "
              f"Hostilidad: {C.RED}{self.ai.hostility:.1f}{C.END}/10.0  |  "
              f"Mutaciones: {C.YELLOW}{self.ai.mutations_count}{C.END}")
        print(f"Pasos: {self.player.steps}  |  "
              f"Retrocesos: {self.player.backtracks}  |  "
              f"Eficiencia: {C.CYAN}{eff:.0f}%{C.END}  |  "
              f"Tiempo: {elapsed:.0f}s")
        print(f"Pos: ({self.player.x},{self.player.y})  →  Meta: {self.goal}")
        
        if self.messages:
            print(f"\n{C.BOLD}─── LOG ───{C.END}")
            for m in self.messages[-4:]:
                print(f"  {m}")
            self.messages.clear()
        
        print(f"\n{C.DIM}WASD = Mover  |  R = Reiniciar piso  |  Q = Rendirse{C.END}")
    
    def run(self):
        clear()
        print(f"""{C.CYAN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        E L   L A B E R I N T O   V I V O                     ║
    ║                                                               ║
    ║  No es un laberinto. Es un organismo.                         ║
    ║  Observa cómo se mueven las paredes cuando no miras.          ║
    ║  Cuanto más rápido avanzas, más te odia.                      ║
    ║                                                               ║
    ║  Encuentra la ◆. Escapa. Repite.                              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        {C.END}""")
        input(f"{C.DIM}Presiona Enter para entrar...{C.END}")
        
        while True:
            self.render()
            
            try:
                key = input(f"\n{C.BOLD}> {C.END}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not key:
                continue
            
            cmd = key[0]
            
            if cmd == 'q':
                print(f"{C.RED}Abandonas el laberinto. Las paredes susurran tu nombre.{C.END}")
                break
            elif cmd == 'r':
                self.maze = Maze(self.maze.w, self.maze.h, self.ai.hostility)
                self.place_entities()
                self.messages.append(f"{C.CYAN}Piso reiniciado.{C.END}")
                continue
            
            dx, dy = 0, 0
            if cmd == 'w': dy = -1
            elif cmd == 's': dy = 1
            elif cmd == 'a': dx = -1
            elif cmd == 'd': dx = 1
            else:
                continue
            
            self.move_player(dx, dy)

if __name__ == "__main__":
    game = Game()
    game.run()
