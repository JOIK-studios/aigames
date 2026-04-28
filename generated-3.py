#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL DUNGEON QUE SE PROGRAMA SOLO
Roguelike metaprogramable. Escribe código (seguro) para reescribir
las reglas de la realidad mientras juegas.
"""

import os
import sys
import time
import random
import math
import ast

# ==================== SEGURIDAD: COMPILADOR DE EXPRESIONES ====================

class SafeMath:
    """Evaluador de expresiones matemáticas sandboxeadas."""
    
    ALLOWED_NAMES = {
        'depth', 'floor', 'level', 'player_level', 'player_hp', 'player_max_hp',
        'player_x', 'player_y', 'enemy_count', 'room_count', 'turn',
    }
    ALLOWED_FUNCS = {'rand', 'min', 'max', 'abs', 'pow', 'sqrt'}
    
    def __init__(self):
        self.cache = {}
    
    def validate(self, expr):
        """Valida sintaxis y seguridad. Devuelve código compilado o raise."""
        if expr in self.cache:
            return self.cache[expr]
        
        try:
            tree = ast.parse(expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Sintaxis inválida: {e}")
        
        self._check_node(tree)
        code = compile(tree, '<dungeon>', 'eval')
        self.cache[expr] = code
        return code
    
    def _check_node(self, node):
        if isinstance(node, ast.Expression):
            self._check_node(node.body)
        elif isinstance(node, ast.BinOp):
            self._check_node(node.left)
            self._check_node(node.right)
        elif isinstance(node, ast.UnaryOp):
            self._check_node(node.operand)
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Solo funciones simples permitidas")
            if node.func.id not in self.ALLOWED_FUNCS:
                raise ValueError(f"Función '{node.func.id}' no permitida")
            for arg in node.args:
                self._check_node(arg)
            if node.keywords:
                raise ValueError("No se permiten argumentos nombrados")
        elif isinstance(node, ast.Name):
            if node.id not in self.ALLOWED_NAMES and node.id not in self.ALLOWED_FUNCS:
                raise ValueError(f"Variable '{node.id}' no permitida")
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("Solo números permitidos")
        elif isinstance(node, ast.Num):  # Python <3.8
            pass
        else:
            raise ValueError(f"Operación no permitida: {type(node).__name__}")
    
    def eval(self, expr, context):
        code = self.validate(expr)
        ctx = dict(context)
        ctx['__builtins__'] = {}
        return eval(code, ctx)

# ==================== COLORES Y UTILS ====================

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
    BG_RED = "\033[41m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== ENTIDADES ====================

class Entity:
    def __init__(self, x, y, char, color, name):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = True
    
    def move(self, dx, dy, dungeon):
        nx, ny = self.x + dx, self.y + dy
        if dungeon.is_walkable(nx, ny):
            self.x, self.y = nx, ny
            return True
        return False

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, '@', C.CYAN, "Jugador")
        self.level = 1
        self.xp = 0
        self.gold = 0
        self.potions = 0
        self.hp = 100
        self.max_hp = 100
        self.dead = False
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

class Enemy(Entity):
    def __init__(self, x, y, hp, damage, name):
        super().__init__(x, y, 'E', C.RED, name)
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.sense = 5
    
    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0

class Item(Entity):
    def __init__(self, x, y, item_type, value):
        char = '$' if item_type == 'gold' else '!' if item_type == 'potion' else '?'
        color = C.YELLOW if item_type == 'gold' else C.GREEN if item_type == 'potion' else C.MAGENTA
        super().__init__(x, y, char, color, item_type)
        self.item_type = item_type
        self.value = value
        self.blocks = False

# ==================== DUNGEON ====================

class Dungeon:
    def __init__(self, width=60, height=22):
        self.w = width
        self.h = height
        self.tiles = [['#' for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.visible = [[False for _ in range(width)] for _ in range(height)]
        self.explored = [[False for _ in range(width)] for _ in range(height)]
    
    def is_walkable(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.tiles[y][x] in ('.', '>', '<')
        return False
    
    def carve_room(self, x1, y1, x2, y2):
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                self.tiles[y][x] = '.'
        self.rooms.append((x1, y1, x2, y2))
    
    def carve_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)+1):
            if self.tiles[y][x] == '#':
                self.tiles[y][x] = '.'
    
    def carve_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2)+1):
            if self.tiles[y][x] == '#':
                self.tiles[y][x] = '.'
    
    def place_stairs(self):
        if self.rooms:
            r = self.rooms[-1]
            cx, cy = (r[0]+r[2])//2, (r[1]+r[3])//2
            self.tiles[cy][cx] = '>'
            return (cx, cy)
        return None
    
    def compute_fov(self, px, py, radius):
        for y in range(self.h):
            for x in range(self.w):
                self.visible[y][x] = False
        
        for y in range(self.h):
            for x in range(self.w):
                if math.hypot(x-px, y-py) <= radius:
                    # Raycasting simple
                    if self._has_line_of_sight(px, py, x, y):
                        self.visible[y][x] = True
                        self.explored[y][x] = True
    
    def _has_line_of_sight(self, x0, y0, x1, y1):
        # Bresenham simplificado
        dx, dy = abs(x1-x0), abs(y1-y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if x0 == x1 and y0 == y1:
                return True
            if self.tiles[y0][x0] == '#' and (x0 != x1 or y0 != y1):
                # Paredes bloquean al final del rayo pero no el propio tile objetivo
                pass
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
            if not (0 <= x0 < self.w and 0 <= y0 < self.h):
                return False
        return True

# ==================== MOTOR DE MÓDULOS ====================

class CodeDungeon:
    DEFAULTS = {
        'mapgen': {
            'room_count': '3 + depth',
            'room_size_min': '3',
            'room_size_max': '5 + depth // 2',
            'corridor_twist': 'depth > 3',
        },
        'spawner': {
            'enemy_count': '2 + depth * 2',
            'enemy_hp': '8 + depth * 5',
            'enemy_damage': '1 + depth * 1',
            'enemy_sense': '4 + depth',
        },
        'loot': {
            'gold_min': '5 + depth * 3',
            'gold_max': '15 + depth * 5',
            'potion_chance': '0.15 + depth * 0.02',
        },
        'combat': {
            'player_damage': '5 + player_level * 2',
            'crit_chance': '0.05',
            'enemy_damage': '2 + depth * 1',
        },
        'player': {
            'max_hp': '100 + player_level * 10',
            'regen': '0',
            'sight_radius': '6',
        }
    }
    
    def __init__(self):
        self.safe = SafeMath()
        self.modules = {mod: dict(vals) for mod, vals in self.DEFAULTS.items()}
        self.depth = 1
        self.turn = 0
        self.dungeon = None
        self.player = None
        self.enemies = []
        self.items = []
        self.stairs_pos = None
        self.messages = []
        self.console_mode = False
    
    def get_context(self, extra=None):
        ctx = {
            'depth': self.depth,
            'floor': self.depth,
            'level': self.depth,
            'player_level': self.player.level if self.player else 1,
            'player_hp': self.player.hp if self.player else 100,
            'player_max_hp': self.player.max_hp if self.player else 100,
            'player_x': self.player.x if self.player else 0,
            'player_y': self.player.y if self.player else 0,
            'turn': self.turn,
            'rand': lambda a, b: random.randint(a, b),
            'min': min, 'max': max, 'abs': abs, 'pow': pow, 'sqrt': math.sqrt,
        }
        if extra:
            ctx.update(extra)
        return ctx
    
    def eval_mod(self, module, key, extra_context=None):
        expr = self.modules[module][key]
        try:
            return self.safe.eval(expr, self.get_context(extra_context))
        except Exception as e:
            self.messages.append(f"{C.RED}BUG en {module}.{key}: {e}{C.END}")
            # Fallback a default
            return self.safe.eval(self.DEFAULTS[module][key], self.get_context(extra_context))
    
    def generate_floor(self):
        self.messages.append(f"{C.CYAN}Generando piso {self.depth}...{C.END}")
        
        # Parámetros del mapa desde código
        room_count = int(self.eval_mod('mapgen', 'room_count'))
        rmin = int(self.eval_mod('mapgen', 'room_size_min'))
        rmax = int(self.eval_mod('mapgen', 'room_size_max'))
        
        self.dungeon = Dungeon()
        attempts = 0
        while len(self.dungeon.rooms) < room_count and attempts < 200:
            attempts += 1
            w = random.randint(rmin, rmax)
            h = random.randint(rmin, rmax)
            x = random.randint(1, self.dungeon.w - w - 2)
            y = random.randint(1, self.dungeon.h - h - 2)
            new_room = (x, y, x+w, y+h)
            
            # Overlap check
            overlap = False
            for r in self.dungeon.rooms:
                if not (new_room[2] < r[0]-1 or new_room[0] > r[2]+1 or 
                        new_room[3] < r[1]-1 or new_room[1] > r[3]+1):
                    overlap = True
                    break
            if not overlap:
                self.dungeon.carve_room(*new_room)
                if len(self.dungeon.rooms) > 1:
                    prev = self.dungeon.rooms[-2]
                    pcx, pcy = (prev[0]+prev[2])//2, (prev[1]+prev[3])//2
                    ncx, ncy = (new_room[0]+new_room[2])//2, (new_room[1]+new_room[3])//2
                    if random.random() < 0.5:
                        self.dungeon.carve_h_corridor(pcx, ncx, pcy)
                        self.dungeon.carve_v_corridor(pcy, ncy, ncx)
                    else:
                        self.dungeon.carve_v_corridor(pcy, ncy, pcx)
                        self.dungeon.carve_h_corridor(pcx, ncx, ncy)
        
        # Stairs
        self.stairs_pos = self.dungeon.place_stairs()
        
        # Player start
        if self.dungeon.rooms:
            r = self.dungeon.rooms[0]
            px, py = (r[0]+r[2])//2, (r[1]+r[3])//2
            if self.player is None:
                self.player = Player(px, py)
            else:
                self.player.x, self.player.y = px, py
        
        # Spawn enemies
        self.enemies = []
        ecount = int(self.eval_mod('spawner', 'enemy_count'))
        for _ in range(ecount):
            if len(self.dungeon.rooms) > 1:
                r = random.choice(self.dungeon.rooms[1:])
                ex = random.randint(r[0]+1, r[2]-1)
                ey = random.randint(r[1]+1, r[3]-1)
                ehp = int(self.eval_mod('spawner', 'enemy_hp'))
                edmg = int(self.eval_mod('spawner', 'enemy_damage'))
                e = Enemy(ex, ey, ehp, edmg, f"Bug#{self.depth}-{_}")
                e.sense = int(self.eval_mod('spawner', 'enemy_sense'))
                self.enemies.append(e)
        
        # Spawn loot
        self.items = []
        potion_chance = self.eval_mod('loot', 'potion_chance')
        for r in self.dungeon.rooms:
            if random.random() < 0.4:
                ix = random.randint(r[0]+1, r[2]-1)
                iy = random.randint(r[1]+1, r[3]-1)
                if random.random() < potion_chance:
                    self.items.append(Item(ix, iy, 'potion', 25))
                else:
                    gmin = int(self.eval_mod('loot', 'gold_min'))
                    gmax = int(self.eval_mod('loot', 'gold_max'))
                    self.items.append(Item(ix, iy, 'gold', random.randint(gmin, gmax)))
        
        self.apply_player_stats()
    
    def apply_player_stats(self):
        if not self.player:
            return
        new_max = int(self.eval_mod('player', 'max_hp'))
        # Solo aumentar max_hp, no curar completamente al bajar
        ratio = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 1
        self.player.max_hp = new_max
        self.player.hp = min(self.player.max_hp, max(1, int(self.player.max_hp * ratio)))
    
    def player_attack(self, enemy):
        dmg = int(self.eval_mod('combat', 'player_damage'))
        crit = self.eval_mod('combat', 'crit_chance')
        if random.random() < crit:
            dmg = int(dmg * 2)
            self.messages.append(f"{C.YELLOW}¡CRÍTICO! {C.END}")
        enemy.hp -= dmg
        self.messages.append(f"Atacas a {enemy.name} por {dmg} daño.")
        if enemy.hp <= 0:
            self.messages.append(f"{C.GREEN}¡{enemy.name} eliminado!{C.END}")
            self.enemies.remove(enemy)
            self.player.xp += 10 + self.depth * 2
            if self.player.xp >= self.player.level * 50:
                self.player.level += 1
                self.player.xp = 0
                self.messages.append(f"{C.CYAN}¡Subiste a nivel {self.player.level}!{C.END}")
                self.apply_player_stats()
    
    def enemy_attack(self, enemy):
        dmg = int(self.eval_mod('combat', 'enemy_damage'))
        self.player.hp -= dmg
        self.messages.append(f"{C.RED}{enemy.name} te golpea por {dmg}.{C.END}")
        if self.player.hp <= 0:
            self.player.dead = True
    
    def move_enemies(self):
        for e in self.enemies:
            dist = math.hypot(e.x - self.player.x, e.y - self.player.y)
            if dist <= e.sense:
                dx = clamp(self.player.x - e.x, -1, 1)
                dy = clamp(self.player.y - e.y, -1, 1)
                if not e.move(dx, dy, self.dungeon):
                    # Si bloquea (otro enemigo), intentar rodear
                    e.move(random.choice([-1,0,1]), random.choice([-1,0,1]), self.dungeon)
            else:
                e.move(random.choice([-1,0,1]), random.choice([-1,0,1]), self.dungeon)
            
            # Combate por contacto
            if e.x == self.player.x and e.y == self.player.y:
                self.enemy_attack(e)
    
    def use_potion(self):
        if self.player.potions > 0:
            self.player.potions -= 1
            self.player.heal(30)
            self.messages.append(f"{C.GREEN}Bebes poción. HP: {self.player.hp}/{self.player.max_hp}{C.END}")
        else:
            self.messages.append(f"{C.YELLOW}No tienes pociones.{C.END}")
    
    def next_floor(self):
        self.depth += 1
        self.generate_floor()
    
    def update(self, action):
        if self.player.dead:
            return
        
        self.turn += 1
        dx, dy = 0, 0
        
        if action == 'w': dy = -1
        elif action == 's': dy = 1
        elif action == 'a': dx = -1
        elif action == 'd': dx = 1
        elif action == 'p':
            self.use_potion()
            return
        elif action == '>':
            if (self.player.x, self.player.y) == self.stairs_pos:
                self.messages.append(f"{C.CYAN}Desciendes al piso {self.depth+1}...{C.END}")
                self.next_floor()
                return
            else:
                self.messages.append(f"{C.YELLOW}No hay escaleras aquí.{C.END}")
                return
        else:
            return
        
        # Movimiento jugador
        target_x, target_y = self.player.x + dx, self.player.y + dy
        
        # Combate
        enemy = None
        for e in self.enemies:
            if e.x == target_x and e.y == target_y:
                enemy = e
                break
        
        if enemy:
            self.player_attack(enemy)
        else:
            self.player.move(dx, dy, self.dungeon)
        
        # Recoger items
        for item in list(self.items):
            if item.x == self.player.x and item.y == self.player.y:
                if item.item_type == 'gold':
                    self.player.gold += item.value
                    self.messages.append(f"{C.YELLOW}Recoges {item.value} oro.{C.END}")
                elif item.item_type == 'potion':
                    self.player.potions += 1
                    self.messages.append(f"{C.GREEN}Recoges poción.{C.END}")
                self.items.remove(item)
        
        # Regen
        regen = self.eval_mod('player', 'regen')
        if regen > 0:
            self.player.heal(regen)
        
        # Enemigos
        if not self.player.dead:
            self.move_enemies()
        
        # FOV
        sight = int(self.eval_mod('player', 'sight_radius'))
        self.dungeon.compute_fov(self.player.x, self.player.y, sight)
    
    # ==================== MODO CONSOLA ====================
    
    def console(self):
        self.console_mode = True
        while self.console_mode:
            clear()
            print(f"{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════════╗")
            print(f"║         T E R M I N A L   D E   S I S T E M A               ║")
            print(f"╠══════════════════════════════════════════════════════════════╣{C.END}")
            print(f"{C.DIM}Escribe código para reescribir la realidad.{C.END}")
            print(f"{C.YELLOW}Variables: depth, player_level, player_hp, rand(min,max){C.END}")
            print(f"{C.YELLOW}Comandos: modules, show <mod>, set <mod>.<key> = <expr>, reset, exit{C.END}")
            print()
            
            cmd = input(f"{C.GREEN}>>> {C.END}").strip()
            if not cmd:
                continue
            
            parts = cmd.split()
            base = parts[0].lower()
            
            if base == 'exit' or base == 'resume':
                self.console_mode = False
            elif base == 'modules':
                for mod in self.modules:
                    print(f"  {C.CYAN}{mod}{C.END}")
            elif base == 'show' and len(parts) >= 2:
                mod = parts[1]
                if mod in self.modules:
                    print(f"\n{C.BOLD}[{mod}]{C.END}")
                    for k, v in self.modules[mod].items():
                        marker = f"{C.GREEN}*{C.END}" if v != self.DEFAULTS[mod][k] else " "
                        print(f"  {marker} {k} = {v}")
                else:
                    print(f"{C.RED}Módulo no encontrado.{C.END}")
            elif base == 'set':
                # set mapgen.room_count = depth + 5
                try:
                    rest = cmd[3:].strip()  # quitar "set"
                    left, right = rest.split('=', 1)
                    left = left.strip()
                    right = right.strip()
                    mod_key = left.split('.')
                    if len(mod_key) != 2:
                        raise ValueError("Formato: set modulo.clave = expr")
                    mod, key = mod_key
                    if mod not in self.modules:
                        raise ValueError(f"Módulo '{mod}' no existe")
                    
                    # Validar
                    self.safe.validate(right)
                    
                    old = self.modules[mod][key]
                    self.modules[mod][key] = right
                    print(f"{C.GREEN}✓ {mod}.{key} = {right}{C.END}")
                    print(f"  (anterior: {old})")
                    
                    # Aplicar cambios inmediatos si es posible
                    if mod == 'player':
                        self.apply_player_stats()
                    
                except Exception as e:
                    print(f"{C.RED}Error: {e}{C.END}")
            elif base == 'reset':
                self.modules = {mod: dict(vals) for mod, vals in self.DEFAULTS.items()}
                self.apply_player_stats()
                print(f"{C.YELLOW}Módulos restaurados a valores de fábrica.{C.END}")
            else:
                print(f"{C.RED}Comando desconocido.{C.END}")
            
            input(f"\n{C.DIM}Enter para continuar...{C.END}")

# ==================== RENDERIZADO ====================

def render(game):
    clear()
    d = game.dungeon
    p = game.player
    
    print(f"{C.BOLD}{C.WHITE}╔{'═'*(d.w+2)}╗{C.END}")
    
    for y in range(d.h):
        row = [f"{C.CYAN}║{C.END} "]
        for x in range(d.w):
            char = ' '
            color = C.DIM
            
            if d.visible[y][x] or d.explored[y][x]:
                tile = d.tiles[y][x]
                if tile == '#':
                    char = '█'
                    color = C.WHITE
                elif tile == '.':
                    char = '·'
                    color = C.DIM
                elif tile == '>':
                    char = '>'
                    color = C.MAGENTA
                    if not d.visible[y][x]:
                        color = C.DIM
                
                # Entidades solo si visibles
                if d.visible[y][x]:
                    for e in game.enemies:
                        if e.x == x and e.y == y:
                            char = e.char
                            color = e.color
                    for item in game.items:
                        if item.x == x and item.y == y:
                            char = item.char
                            color = item.color
                    if p.x == x and p.y == y:
                        char = p.char
                        color = p.color
            else:
                char = ' '
                color = C.DIM
            
            row.append(f"{color}{char}{C.END}")
        row.append(f"{C.CYAN} ║{C.END}")
        print(''.join(row))
    
    print(f"{C.BOLD}{C.WHITE}╚{'═'*(d.w+2)}╝{C.END}")
    
    # UI
    hp_bar = int((p.hp / p.max_hp) * 20) if p.max_hp > 0 else 0
    bar = f"{C.GREEN}{'█'*hp_bar}{C.RED}{'░'*(20-hp_bar)}{C.END}"
    print(f"\n{C.BOLD}Piso {game.depth}  |  {p.name}  Lv.{p.level}{C.END}")
    print(f"HP: {bar} {p.hp}/{p.max_hp}  |  Oro: {C.YELLOW}{p.gold}{C.END}  |  Pociones: {C.GREEN}{p.potions}{C.END}  |  XP: {p.xp}/{p.level*50}")
    print(f"{C.DIM}WASD=Mover  P=Poción  >=Escaleras  ~=Terminal{C.END}")
    
    # Mensajes
    if game.messages:
        print(f"\n{C.BOLD}─── LOG ───{C.END}")
        for m in game.messages[-5:]:
            print(f"  {m}")
        game.messages.clear()

# ==================== JUEGO ====================

def game_over(game):
    clear()
    print(f"""{C.RED}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║                    S Y S T E M   C R A S H                    ║
    ║                                                               ║
    ║              Tu código ha dejado de ejecutarse.               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    {C.END}""")
    print(f"{C.YELLOW}Piso alcanzado: {game.depth}")
    print(f"Oro total: {game.player.gold}")
    print(f"Nivel: {game.player.level}{C.END}")
    print(f"\n{C.DIM}Las regias que escribiste persisten en el stack del infierno...{C.END}")

def main():
    clear()
    print(f"""{C.CYAN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     E L   D U N G E O N   Q U E   S E   P R O G R A M A      ║
    ║                                                               ║
    ║  Eres tanto el jugador como el arquitecto. Cada piso es       ║
    ║  generado por funciones que PUEDES REESCRIBIR en tiempo real. ║
    ║                                                               ║
    ║  Presiona ~ (tilde) para abrir la terminal del sistema.       ║
    ║  Modifica las fórmulas. Rompe el juego a tu favor...          ║
    ║  ...o descubre cómo te rompe a ti.                            ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    {C.END}""")
    input(f"{C.DIM}Presiona Enter para compilar la realidad...{C.END}")
    
    game = CodeDungeon()
    game.generate_floor()
    
    while True:
        if game.player.dead:
            game_over(game)
            break
        
        render(game)
        
        try:
            key = input(f"{C.BOLD}> {C.END}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        
        if key == '~' or key == '`':
            game.console()
        elif key in ('w','a','s','d','p','>'):
            game.update(key)
        else:
            pass

if __name__ == "__main__":
    main()
