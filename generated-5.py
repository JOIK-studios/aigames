#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL JUEGO QUE SE ROMPE
Un platformer donde los bugs son features.
Empieza normal. Termina en caos.
"""

import os
import sys
import time
import random

# ==================== VISUALES ====================

class C:
    END = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== NIVELES ====================

LEVELS = [
    # Nivel 0: Tutorial (Normal)
    {
        "name": "0x00: Boot Sequence",
        "map": [
            "####################",
            "#                  #",
            "#               X  #",
            "#            ##### #",
            "#                  #",
            "#                  #",
            "#@                 #",
            "####################",
        ],
        "hint": "Usa A/D para moverte, W/ESPACIO para saltar. Llega a la X.",
    },
    # Nivel 1: Input Buffer Overflow
    {
        "name": "0x01: Buffer Overflow",
        "map": [
            "####################",
            "#               X  #",
            "#            ####  #",
            "#            ####  #",
            "#            ####  #",
            "#            ####  #",
            "#@           ####  #",
            "####################",
        ],
        "hint": "Este muro es demasiado alto para un salto normal...",
    },
    # Nivel 2: Floating Point Error (gravedad baja)
    {
        "name": "0x02: Floating Point",
        "map": [
            "########################################",
            "#                                 X    #",
            "#                                      #",
            "#                                      #",
            "#                                      #",
            "#                                      #",
            "#@                                     #",
            "########################################",
        ],
        "hint": "Un abismo imposible de cruzar... a menos que la física falle.",
    },
    # Nivel 3: Memory Leak (paredes fantasma)
    {
        "name": "0x03: Memory Leak",
        "map": [
            "####################",
            "#X                 #",
            "#######░########## #",
            "#                  #",
            "#                  #",
            "#                  #",
            "#@                 #",
            "####################",
        ],
        "hint": "Algunos objetos no inicializan correctamente sus colisiones.",
    },
    # Nivel 4: Stack Overflow (gravedad invertida)
    {
        "name": "0x04: Stack Overflow",
        "map": [
            "####################",
            "#                  #",
            "#   X              #",
            "#   #              #",
            "#   #              #",
            "#   #              #",
            "#   #     @        #",
            "####################",
        ],
        "hint": "La gravedad ha sido comprometida. Caes hacia arriba.",
    },
    # Nivel 5: Kernel Panic (todo roto)
    {
        "name": "0x05: Kernel Panic",
        "map": [
            "#######################",
            "#  ^             X    #",
            "#  #  ░░░  ^   ####   #",
            "#     ####  #         #",
            "#  ^        #  ░░░    #",
            "#  #        #  ####   #",
            "#@     ^              #",
            "#######################",
        ],
        "hint": "Todo falla. Usa todo lo que has aprendido.",
    },
]

# ==================== MOTOR DE BUGS ====================

class BugEngine:
    def __init__(self):
        self.level = 0
        self.active = {
            'input_buffer_overflow': False,  # Saltar infinitamente spameando
            'low_gravity': False,            # Gravedad reducida
            'memory_leak': False,            # Paredes fantasma (░ no colisionan)
            'inverted_gravity': False,       # Gravedad negativa
            'sprite_corruption': False,      # Caracteres cambian aleatoriamente
            'input_swap': False,             # A y D intercambiados
        }
        self.error_log = []
        self.corruption = 0.0  # 0.0 a 1.0
    
    def activate(self, bug_name, message):
        if not self.active.get(bug_name, False):
            self.active[bug_name] = True
            self.error_log.append(message)
            self.corruption = min(1.0, self.corruption + 0.2)
    
    def corrupt_char(self, char):
        if not self.active['sprite_corruption']:
            return char
        if char in ('#', '░', '@', 'X', '^'):
            if random.random() < self.corruption:
                glitches = ['▓', '▒', '█', '▀', '▄', '▌', '▐', '░', '▒', '¿', '¤', 'Ø']
                return random.choice(glitches)
        return char

# ==================== FÍSICAS Y JUGADOR ====================

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.dead = False
    
    def reset(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.dead = False

class Game:
    # Constantes físicas
    GRAVITY_NORMAL = 0.25
    GRAVITY_LOW = 0.04
    GRAVITY_INVERTED = -0.25
    MOVE_FORCE = 0.6
    JUMP_FORCE = 1.4
    FRICTION = 0.85
    TICKS_PER_INPUT = 6
    
    def __init__(self):
        self.bugs = BugEngine()
        self.current_level = 0
        self.player = Player(0, 0)
        self.map_data = []
        self.width = 0
        self.height = 0
        self.start_pos = (0, 0)
        self.end_pos = (0, 0)
        self.messages = []
        self.load_level(0)
    
    def load_level(self, idx):
        if idx >= len(LEVELS):
            self.win_game()
            return False
        
        self.current_level = idx
        data = LEVELS[idx]
        self.map_data = [list(row) for row in data["map"]]
        self.height = len(self.map_data)
        self.width = max(len(r) for r in self.map_data)
        
        # Normalizar ancho
        for row in self.map_data:
            while len(row) < self.width:
                row.append(' ')
        
        # Encontrar posiciones
        for y, row in enumerate(self.map_data):
            for x, c in enumerate(row):
                if c == '@':
                    self.start_pos = (x, y)
                    row[x] = ' '
                elif c == 'X':
                    self.end_pos = (x, y)
        
        self.player.reset(*self.start_pos)
        self.messages = []
        
        # Activar bugs progresivos
        if idx >= 1:
            self.bugs.activate('input_buffer_overflow', 
                f"{C.YELLOW}[WARNING] Input buffer not clearing. Multiple jump events detected.{C.END}")
        if idx >= 2:
            self.bugs.activate('low_gravity',
                f"{C.YELLOW}[ERROR] Floating point precision loss in gravity constant.{C.END}")
        if idx >= 3:
            self.bugs.activate('memory_leak',
                f"{C.RED}[CRITICAL] Memory leak in collision module. Objects uninitialized.{C.END}")
        if idx >= 4:
            self.bugs.activate('inverted_gravity',
                f"{C.RED}[FATAL] Stack overflow in physics thread. Reversing gravity vector.{C.END}")
        if idx >= 5:
            self.bugs.activate('sprite_corruption',
                f"{C.MAGENTA}[KERNEL PANIC] Sprite table corrupted. Rendering undefined.{C.END}")
            self.bugs.activate('input_swap',
                f"{C.MAGENTA}[SEGFAULT] Input mapper pointer corrupted. Keys remapped.{C.END}")
        
        return True
    
    def get_tile(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            return self.map_data[iy][ix]
        return '#'
    
    def is_solid(self, x, y):
        tile = self.get_tile(x, y)
        if tile == '#':
            return True
        if tile == '░' and self.bugs.active['memory_leak']:
            return False  # Bug: pared fantasma no colisiona
        return False
    
    def is_spike(self, x, y):
        return self.get_tile(x, y) == '^'
    
    def check_win(self):
        return (int(self.player.x), int(self.player.y)) == self.end_pos
    
    def physics_tick(self):
        p = self.player
        
        # Gravedad
        if self.bugs.active['inverted_gravity']:
            p.vy += self.GRAVITY_INVERTED
        elif self.bugs.active['low_gravity']:
            p.vy += self.GRAVITY_LOW
        else:
            p.vy += self.GRAVITY_NORMAL
        
        # Movimiento
        new_x = p.x + p.vx
        new_y = p.y + p.vy
        
        # Colisión eje X
        if not self.is_solid(new_x, p.y):
            p.x = new_x
        else:
            p.vx = 0
        
        # Colisión eje Y
        if not self.is_solid(p.x, new_y):
            p.y = new_y
            p.on_ground = False
        else:
            # Colisión vertical
            if self.bugs.active['inverted_gravity']:
                # En gravedad invertida, "suelo" es el techo (vy < 0)
                if p.vy < 0:
                    p.on_ground = True
            else:
                if p.vy > 0:
                    p.on_ground = True
            p.vy = 0
        
        # Fricción
        p.vx *= self.FRICTION
        
        # Límites del mundo
        p.x = max(0.5, min(self.width - 1.5, p.x))
        p.y = max(0.5, min(self.height - 1.5, p.y))
        
        # Spikes
        if self.is_spike(p.x, p.y):
            p.dead = True
        
        # Victoria
        if self.check_win():
            return True
        return False
    
    def do_action(self, action):
        p = self.player
        
        # Input swap bug
        if self.bugs.active['input_swap']:
            if action == 'a': action = 'd'
            elif action == 'd': action = 'a'
        
        if action == 'a':
            p.vx -= self.MOVE_FORCE
        elif action == 'd':
            p.vx += self.MOVE_FORCE
        elif action in ('w', ' '):
            # Bug de input buffer: siempre añade impulso, no solo en suelo
            if self.bugs.active['input_buffer_overflow']:
                p.vy -= self.JUMP_FORCE * 0.7  # Spamear salto = volar
                p.on_ground = False
            else:
                if p.on_ground:
                    p.vy -= self.JUMP_FORCE
                    p.on_ground = False
        elif action == 's':
            if self.bugs.active['inverted_gravity']:
                p.vy -= 0.5  # "Caer" hacia arriba más rápido
            else:
                p.vy += 0.5
        elif action == 'r':
            self.player.reset(*self.start_pos)
            self.messages.append(f"{C.CYAN}Reiniciando nivel...{C.END}")
            return False
        
        # Simular múltiples ticks de física por input
        for _ in range(self.TICKS_PER_INPUT):
            if self.physics_tick():
                return True  # Victoria
            if p.dead:
                return False
        
        return False
    
    def render(self):
        clear()
        level_data = LEVELS[self.current_level]
        
        # Banner
        print(f"{C.CYAN}{C.BOLD}╔{'═'*(self.width+2)}╗{C.END}")
        
        # Mapa
        for y in range(self.height):
            row = [f"{C.CYAN}║{C.END}"]
            for x in range(self.width):
                tile = self.map_data[y][x]
                
                # Jugador
                if int(self.player.x) == x and int(self.player.y) == y:
                    row.append(f"{C.GREEN}@{C.END}")
                else:
                    # Corrupción visual
                    display = self.bugs.corrupt_char(tile)
                    if tile == 'X':
                        row.append(f"{C.YELLOW}{C.BOLD}{display}{C.END}")
                    elif tile == '^':
                        row.append(f"{C.RED}{display}{C.END}")
                    elif tile == '░':
                        row.append(f"{C.DIM}{display}{C.END}")
                    elif tile == '#':
                        row.append(f"{C.WHITE}{display}{C.END}")
                    else:
                        row.append(display)
            row.append(f"{C.CYAN}║{C.END}")
            print(''.join(row))
        
        print(f"{C.CYAN}{C.BOLD}╚{'═'*(self.width+2)}╝{C.END}")
        
        # UI
        print(f"\n{C.BOLD}{level_data['name']}{C.END}")
        print(f"{C.DIM}{level_data['hint']}{C.END}")
        print(f"Pos: ({self.player.x:.1f}, {self.player.y:.1f}) | "
              f"Vel: ({self.player.vx:.1f}, {self.player.vy:.1f}) | "
              f"Ground: {self.player.on_ground}")
        
        # Errores acumulados
        if self.bugs.error_log:
            print(f"\n{C.RED}{C.BOLD}═══ SYSTEM LOGS ═══{C.END}")
            for msg in self.bugs.error_log[-4:]:
                print(f"  {msg}")
        
        # Mensajes temporales
        if self.messages:
            for m in self.messages[-2:]:
                print(m)
            self.messages.clear()
        
        print(f"\n{C.DIM}A=izq  D=der  W/espacio=saltar  S=caer rápido  R=reiniciar  Q=salir{C.END}")
    
    def death_screen(self):
        print(f"\n{C.RED}{C.BOLD}")
        print("    ╔═══════════════════════════════════════╗")
        print("    ║     E R R O R   D E   S E G M E N T O   ║")
        print("    ║                                       ║")
        print("    ║  Has tocado código letal.             ║")
        print("    ║  Reiniciando instancia...             ║")
        print("    ╚═══════════════════════════════════════╝")
        print(f"{C.END}")
        time.sleep(1)
        self.player.reset(*self.start_pos)
    
    def win_level(self):
        print(f"\n{C.GREEN}{C.BOLD}")
        print("    ╔═══════════════════════════════════════╗")
        print("    ║     S E C T O R   C O M P L E T A D O   ║")
        print("    ╚═══════════════════════════════════════╝")
        print(f"{C.END}")
        time.sleep(1.5)
        if not self.load_level(self.current_level + 1):
            return False
        return True
    
    def win_game(self):
        clear()
        print(f"""
{C.GREEN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           E S C A P E   D E   L A   M A T R I Z               ║
    ║                                                               ║
    ║  Has explotado todos los bugs. Has roto el juego.             ║
    ║  Ya no eres un sprite en un bucle.                            ║
    ║  Eres el error que escapó.                                    ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    {C.DIM}El programa ha terminado, pero tú... persistes.{C.END}
        """)
        sys.exit(0)
    
    def run(self):
        clear()
        print(f"""{C.CYAN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        E L   J U E G O   Q U E   S E   R O M P E             ║
    ║                                                               ║
    ║  Un platformer normal. Plataformas, saltos, metas.            ║
    ║  Nada puede salir mal.                                        ║
    ║  Definitivamente no hay bugs.                                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        {C.END}""")
        input(f"{C.DIM}Presiona Enter para iniciar secuencia...{C.END}")
        
        while True:
            self.render()
            
            try:
                key = input(f"{C.BOLD}> {C.END}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            
            if key == 'q':
                print(f"{C.RED}Abortando ejecución...{C.END}")
                break
            
            if self.player.dead:
                self.death_screen()
                continue
            
            if key in ('a', 'd', 'w', ' ', 's', 'r'):
                won = self.do_action(key)
                if won:
                    if not self.win_level():
                        break

if __name__ == "__main__":
    game = Game()
    game.run()
