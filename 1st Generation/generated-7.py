#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MENTE FRAGMENTADA
Un solo input. Varios cuerpos. Cada mente lo interpreta a su manera.
Resuelve puzzles sincronizando almas rotas.
"""

import os
import sys

class C:
    END = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"
    WHITE = "\033[97m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== PERSONAJES Y TRASTORNOS ====================

class Fragment:
    def __init__(self, name, char, goal_char, color, x, y, gx, gy, disorder):
        self.name = name
        self.char = char          # Símbolo en mapa
        self.goal_char = goal_char
        self.color = color
        self.x = x
        self.y = y
        self.gx = gx
        self.gy = gy
        self.disorder = disorder  # función de transformación
        self.stunned = 0
        self.at_goal = False
    
    def interpret(self, inp):
        """Recibe w/a/s/d y devuelve (dx,dy) según su trastorno."""
        base = {'w': (0,-1), 'a': (-1,0), 's': (0,1), 'd': (1,0)}
        if inp not in base:
            return (0,0)
        
        dx, dy = base[inp]
        
        if self.disorder == "normal":
            return (dx, dy)
        elif self.disorder == "inverted":
            return (-dx, -dy)
        elif self.disorder == "mirror_x":
            return (-dx, dy)
        elif self.disorder == "mirror_y":
            return (dx, -dy)
        elif self.disorder == "rotated_90":
            # W->D, D->S, S->A, A->W  (rotación horaria)
            rot = {'w': (1,0), 'd': (0,1), 's': (-1,0), 'a': (0,-1)}
            return rot[inp]
        elif self.disorder == "rotated_270":
            # W->A, A->S, S->D, D->W
            rot = {'w': (-1,0), 'a': (0,1), 's': (1,0), 'd': (0,-1)}
            return rot[inp]
        elif self.disorder == "double":
            return (dx*2, dy*2)
        elif self.disorder == "lazy":
            # Solo se mueve cada 2 inputs (alternando)
            self.stunned = 1 - self.stunned
            return (dx, dy) if self.stunned == 0 else (0,0)
        elif self.disorder == "phantom":
            # Se mueve normal, pero puede atravesar paredes (manejado en game)
            return (dx, dy)
        elif self.disorder == "stuck_x":
            # Solo se mueve en X, ignora W/S
            return (dx, 0)
        elif self.disorder == "stuck_y":
            # Solo se mueve en Y, ignora A/D
            return (0, dy)
        return (dx, dy)

# ==================== NIVELES ====================

LEVELS = [
    # Nivel 0: El Despertar
    {
        "name": "Sala 0: El Despertar",
        "hint": "Dos voces. Una escucha bien. La otra al revés.",
        "map": [
            "##########",
            "#A.......#",
            "#........#",
            "#........#",
            "#........#",
            "#........#",
            "#.......B#",
            "#........#",
            "#.......b#",
            "#........#",
            "#a.......#",
            "##########",
        ],
        "fragments": [
            Fragment("Eco",      'A', 'a', C.CYAN,    1, 1, 1, 10, "normal"),
            Fragment("Sombra",   'B', 'b', C.MAGENTA, 8, 6, 8, 8,  "inverted"),
        ],
    },
    # Nivel 1: El Espejo Roto
    {
        "name": "Sala 1: El Espejo Roto",
        "hint": "Uno se refleja en el eje X. Otro en el Y. La meta es el reflejo.",
        "map": [
            "############",
            "#A.........#",
            "#..........#",
            "#...####...#",
            "#...#..#...#",
            "#...#..#...#",
            "#...####...#",
            "#..........#",
            "#.........B#",
            "#..........#",
            "#a........b#",
            "############",
        ],
        "fragments": [
            Fragment("Verdad",  'A', 'a', C.GREEN,  1, 1, 1, 10, "normal"),
            Fragment("Farsa",   'B', 'b', C.RED,    10, 8, 10, 10, "mirror_x"),
        ],
    },
    # Nivel 2: La Máquina
    {
        "name": "Sala 2: La Máquina",
        "hint": "Un cuerpo gira 90°. Otro solo avanza en línea recta. Sincroniza.",
        "map": [
            "##############",
            "#A...........#",
            "#............#",
            "#######......#",
            "#......####..#",
            "#.........#..#",
            "#.........#..#",
            "#..####...#..#",
            "#..#.......#.#",
            "#..#.......#B#",
            "#..#.......#b#",
            "#a.#.......###",
            "##############",
        ],
        "fragments": [
            Fragment("Mente",   'A', 'a', C.CYAN,    1, 1, 1, 11, "normal"),
            Fragment("Engranaje",'B','b', C.YELLOW,  12, 9, 12, 10, "rotated_90"),
        ],
    },
    # Nivel 3: Botones y Puertas
    {
        "name": "Sala 3: El Fantasma y el Interruptor",
        "hint": "El fantasma atraviesa paredes pero no pisa botones. El sólido sí.",
        "map": [
            "##############",
            "#A...........#",
            "#............#",
            "#..#######...#",
            "#..#.....#...#",
            "#..#.!...#...#",
            "#..#######...#",
            "#............#",
            "#...=........#",
            "#...=........#",
            "#...=.......B#",
            "#a..=.......b#",
            "##############",
        ],
        "fragments": [
            Fragment("Cuerpo",   'A', 'a', C.GREEN,   1, 1, 1, 11, "normal"),
            Fragment("Espectro", 'B', 'b', C.BLUE,    12, 10, 12, 11, "phantom"),
        ],
        "buttons": [(6, 5)],  # x,y
        "doors": [(4,8),(4,9),(4,10),(4,11)],  # se abren con botón
    },
    # Nivel 4: Cuatro Almas
    {
        "name": "Sala 4: Coro Descoordinado",
        "hint": "Normal. Invertido. Rotado 270°. Solo eje Y. Cuatro mentes, un solo grito.",
        "map": [
            "##################",
            "#A...............#",
            "#................#",
            "#...####...####..#",
            "#...#........#...#",
            "#...#...B....#...#",
            "#...#........#...#",
            "#...####...####..#",
            "#................#",
            "#.......C........#",
            "#................#",
            "#...####...####..#",
            "#...#........#...#",
            "#...#...D....#...#",
            "#...#........#...#",
            "#...####...####..#",
            "#................#",
            "#a....b....c....d#",
            "##################",
        ],
        "fragments": [
            Fragment("Yo",       'A', 'a', C.CYAN,    1, 1, 1, 17, "normal"),
            Fragment("Anti-Yo",  'B', 'b', C.RED,     8, 5, 6, 17, "inverted"),
            Fragment("Giro",     'C', 'c', C.YELLOW,  8, 9, 10, 17, "rotated_270"),
            Fragment("Caída",    'D', 'd', C.MAGENTA, 8, 13, 14, 17, "stuck_y"),
        ],
    },
    # Nivel 5: El Caos Perfecto
    {
        "name": "Sala 5: Sincronía Final",
        "hint": "Doble paso. Espejo X. Lazy. Fantasma. Si uno falla, todos mueren.",
        "map": [
            "####################",
            "#A.................#",
            "#..................#",
            "#..####....####....#",
            "#..#..#....#..#....#",
            "#..#.!#....#..#....#",
            "#..####....####....#",
            "#..................#",
            "#.......B..........#",
            "#..................#",
            "#..####....####....#",
            "#..#..#....#..#....#",
            "#..#..#....#..#....#",
            "#..####....####....#",
            "#..................#",
            "#..................#",
            "#.........C........#",
            "#..................#",
            "#a...b.......c.....#",
            "####################",
        ],
        "fragments": [
            Fragment("Prisa",    'A', 'a', C.GREEN,   1, 1, 1, 18, "double"),
            Fragment("Reflejo",  'B', 'b', C.RED,     8, 8, 5, 18, "mirror_x"),
            Fragment("Letargo",  'C', 'c', C.YELLOW,  10, 16, 12, 18, "lazy"),
        ],
        "buttons": [(5, 5)],
        "doors": [(6,11),(6,12),(6,13)],  # bloquean camino de B hacia b
    },
]

# ==================== MOTOR ====================

class Game:
    def __init__(self):
        self.level_idx = 0
        self.load_level(0)
    
    def load_level(self, idx):
        if idx >= len(LEVELS):
            self.win_game()
            return
        
        data = LEVELS[idx]
        self.name = data["name"]
        self.hint = data["hint"]
        self.raw_map = [list(row) for row in data["map"]]
        self.h = len(self.raw_map)
        self.w = max(len(r) for r in self.raw_map)
        
        # Normalizar ancho
        for row in self.raw_map:
            while len(row) < self.w:
                row.append(' ')
        
        self.fragments = [Fragment(f.name, f.char, f.goal_char, f.color, f.x, f.y, f.gx, f.gy, f.disorder) 
                         for f in data["fragments"]]
        
        # Botones y puertas
        self.buttons = set(tuple(b) for b in data.get("buttons", []))
        self.doors = set(tuple(d) for d in data.get("doors", []))
        self.buttons_pressed = set()
        
        self.turn = 0
        self.messages = []
    
    def is_wall(self, x, y, is_phantom=False):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return True
        tile = self.raw_map[y][x]
        if tile == '#':
            return True
        if (x, y) in self.doors and (x, y) not in self.buttons_pressed:
            return True
        return False
    
    def is_spike(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.raw_map[y][x] == '^'
        return False
    
    def check_buttons(self):
        self.buttons_pressed = set()
        for bx, by in self.buttons:
            for f in self.fragments:
                if f.x == bx and f.y == by and f.disorder != "phantom":
                    self.buttons_pressed.add((bx, by))
    
    def move_fragment(self, f, dx, dy):
        nx, ny = f.x + dx, f.y + dy
        
        # Fantasma atraviesa paredes pero no sale del mapa
        if f.disorder == "phantom":
            if 0 <= nx < self.w and 0 <= ny < self.h:
                # No atraviesa puertas cerradas (etéreo pero no tanto)
                if (nx, ny) in self.doors and (nx, ny) not in self.buttons_pressed:
                    pass  # No puede
                else:
                    f.x, f.y = nx, ny
            return
        
        # Doble paso: verificar colisión en cada celda intermedia
        if f.disorder == "double":
            steps = [(f.x + dx//2, f.y + dy//2), (nx, ny)] if (dx !=0 or dy !=0) else []
            valid = True
            for sx, sy in steps:
                if self.is_wall(sx, sy):
                    valid = False
                    break
            if valid and not self.is_spike(nx, ny):
                f.x, f.y = nx, ny
            return
        
        # Movimiento normal
        if not self.is_wall(nx, ny):
            if not self.is_spike(nx, ny):
                f.x, f.y = nx, ny
    
    def update(self, inp):
        self.turn += 1
        moved_any = False
        
        for f in self.fragments:
            dx, dy = f.interpret(inp)
            if dx != 0 or dy != 0:
                self.move_fragment(f, dx, dy)
                moved_any = True
        
        self.check_buttons()
        
        # Verificar victoria
        all_at_goal = True
        for f in self.fragments:
            if f.x == f.gx and f.y == f.gy:
                f.at_goal = True
            else:
                f.at_goal = False
                all_at_goal = False
        
        return all_at_goal
    
    def render(self):
        clear()
        print(f"{C.CYAN}{C.BOLD}╔{'═'*(self.w+2)}╗{C.END}")
        
        # Construir grid visual
        grid = []
        for y in range(self.h):
            row = []
            for x in range(self.w):
                tile = self.raw_map[y][x]
                
                # Prioridad: fragmento > meta > botón/puerta > tile base
                frag_here = None
                for f in self.fragments:
                    if f.x == x and f.y == y:
                        frag_here = f
                        break
                
                if frag_here:
                    sym = frag_here.char
                    col = frag_here.color
                    # Si está en su meta, parpadea
                    if frag_here.at_goal:
                        row.append(f"{C.BOLD}{C.GREEN}{sym}{C.END}")
                    else:
                        row.append(f"{col}{sym}{C.END}")
                else:
                    # Metas
                    goal_here = None
                    for f in self.fragments:
                        if f.gx == x and f.gy == y:
                            goal_here = f
                            break
                    
                    if goal_here:
                        row.append(f"{C.DIM}{goal_here.goal_char}{C.END}")
                    elif (x, y) in self.buttons:
                        pressed = (x,y) in self.buttons_pressed
                        color = C.GREEN if pressed else C.RED
                        sym = '●' if pressed else '!'
                        row.append(f"{color}{sym}{C.END}")
                    elif (x, y) in self.doors:
                        open_door = (x,y) in self.buttons_pressed
                        sym = ' ' if open_door else '='
                        color = C.DIM if open_door else C.YELLOW
                        row.append(f"{color}{sym}{C.END}")
                    elif tile == '^':
                        row.append(f"{C.RED}^{C.END}")
                    elif tile == '#':
                        row.append(f"{C.WHITE}█{C.END}")
                    else:
                        row.append(tile)
            grid.append(row)
        
        for y, row in enumerate(grid):
            line = ''.join(row)
            print(f"{C.CYAN}║{C.END} {line}{C.CYAN} ║{C.END}")
        
        print(f"{C.CYAN}{C.BOLD}╚{'═'*(self.w+2)}╝{C.END}")
        
        # UI
        print(f"\n{C.BOLD}{self.name}{C.END}")
        print(f"{C.DIM}{self.hint}{C.END}")
        print(f"\n{C.YELLOW}Turno: {self.turn}{C.END}")
        
        print(f"\n{C.BOLD}Fragmentos:{C.END}")
        for f in self.fragments:
            status = f"{C.GREEN}✓{C.END}" if f.at_goal else f"{C.RED}○{C.END}"
            disorder_name = {
                "normal": "Normal", "inverted": "Invertido", "mirror_x": "Espejo X",
                "mirror_y": "Espejo Y", "rotated_90": "Giro 90°", "rotated_270": "Giro 270°",
                "double": "Doble paso", "lazy": "Letargo", "phantom": "Fantasma",
                "stuck_x": "Solo X", "stuck_y": "Solo Y",
            }.get(f.disorder, f.disorder)
            print(f"  {status} {f.color}{f.name}{C.END} ({f.char}→{f.goal_char}) [{disorder_name}] "
                  f"pos:({f.x},{f.y}) meta:({f.gx},{f.gy})")
        
        if self.buttons:
            pressed = len(self.buttons_pressed)
            total = len(self.buttons)
            print(f"\n{C.YELLOW}Botones: {pressed}/{total}{C.END}")
        
        print(f"\n{C.DIM}WASD = Mover a todos  |  R = Reiniciar sala  |  Q = Rendirse{C.END}")
    
    def level_complete(self):
        print(f"\n{C.GREEN}{C.BOLD}")
        print("    ╔═══════════════════════════════════════╗")
        print("    ║     S I N C R O N Í A   L O G R A D A   ║")
        print("    ╚═══════════════════════════════════════╝")
        print(f"{C.END}")
        input(f"{C.DIM}Enter para continuar...{C.END}")
        self.load_level(self.level_idx + 1)
    
    def win_game(self):
        clear()
        print(f"""
{C.CYAN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           L A   M E N T E   H A   S A N A D O                 ║
    ║                                                               ║
    ║  Todas las voces cantan al unísono.                           ║
    ║  El caos se ha ordenado en una verdad más grande.             ║
    ║  Ya no eres fragmentos.                                       ║
    ║  Eres uno.                                                    ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    Turnos totales: {self.turn}
    Salas completadas: {len(LEVELS)}
        """)
        sys.exit(0)
    
    def run(self):
        clear()
        print(f"""{C.CYAN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        M E N T E   F R A G M E N T A D A                     ║
    ║                                                               ║
    ║  Despiertas en una sala blanca. No estás solo.                ║
    ║  Hay otros contigo. Pero todos comparten tu voluntad.         ║
    ║  Cuando tú dices 'arriba', uno obedece...                     ║
    ║  ...pero otro cae.                                            ║
    ║                                                               ║
    ║  Sincroniza las mentes. Lleva cada fragmento a su meta.       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        {C.END}""")
        input(f"{C.DIM}Presiona Enter para entrar en la primera sala...{C.END}")
        
        while True:
            self.render()
            
            try:
                inp = input(f"\n{C.BOLD}Comando: {C.END}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not inp:
                continue
            
            cmd = inp[0]
            
            if cmd == 'q':
                print(f"{C.RED}Abandonando el laberinto mental...{C.END}")
                break
            elif cmd == 'r':
                self.load_level(self.level_idx)
                self.messages.append(f"{C.CYAN}Sala reiniciada.{C.END}")
                continue
            
            if cmd in ('w','a','s','d'):
                won = self.update(cmd)
                if won:
                    self.render()
                    self.level_complete()
            else:
                self.messages.append(f"{C.RED}Input no reconocido. Usa WASD.{C.END}")

if __name__ == "__main__":
    game = Game()
    game.run()
