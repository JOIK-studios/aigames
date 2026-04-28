#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECOSISTEMA EVOLUTIVO
Simulación de vida artificial con ADN mutable, selección natural
y modo Dios Caótico. Todo ocurre en la terminal.
"""

import os
import sys
import time
import random
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field

# ==================== UTILIDADES VISUALES ====================

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_BLACK = "\033[40m"
    BG_GREEN = "\033[42m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ==================== ADN Y GENÉTICA ====================

GENE_RANGES = {
    'speed':     (0.5, 3.5),   # Cuántas celdas puede moverse
    'size':      (0.5, 3.0),   # Afecta coste energético y defensa
    'sense':     (1.0, 8.0),   # Radio de detección de comida
    'metabolism':(0.3, 2.0),   # Menor = más eficiente
    'fertility': (0.1, 0.9),   # Probabilidad de reproducirse
    'mut_rate':  (0.01, 0.6),  # Probabilidad base de mutar cada gen
}

@dataclass
class DNA:
    genes: dict = field(default_factory=dict)
    lineage: str = "primordial"
    
    def __post_init__(self):
        if not self.genes:
            self.genes = {k: random.uniform(*r) for k, r in GENE_RANGES.items()}
        else:
            # Asegurar límites
            for k, (lo, hi) in GENE_RANGES.items():
                self.genes[k] = clamp(self.genes.get(k, random.uniform(lo, hi)), lo, hi)
    
    def mutate(self):
        """Crea una copia mutada del ADN."""
        child_genes = {}
        mut_rate = self.genes['mut_rate']
        mutated = False
        
        for k, (lo, hi) in GENE_RANGES.items():
            v = self.genes[k]
            if random.random() < mut_rate:
                # Mutación gaussiana
                delta = random.gauss(0, (hi - lo) * 0.15)
                v = clamp(v + delta, lo, hi)
                mutated = True
            child_genes[k] = v
        
        # Si no mutó ningún gen principal, forzar una micro-mutación
        if not mutated:
            k = random.choice(list(GENE_RANGES.keys()))
            lo, hi = GENE_RANGES[k]
            child_genes[k] = clamp(child_genes[k] + random.gauss(0, (hi-lo)*0.05), lo, hi)
        
        return DNA(genes=child_genes, lineage=self.lineage)
    
    def phenotype_color(self):
        """Genera un color ANSI basado en el genoma."""
        s = sum(self.genes.values())
        hues = [Color.RED, Color.YELLOW, Color.GREEN, Color.CYAN, Color.BLUE, Color.MAGENTA]
        idx = int(s * 1.5) % len(hues)
        return hues[idx]
    
    def species_hash(self):
        """Clasificación burda de 'especie' por rangos de genes."""
        return tuple(int(self.genes[k] * 2) for k in ['size', 'speed', 'sense'])

# ==================== CRIATURA ====================

@dataclass
class Creature:
    id: int
    x: int
    y: int
    dna: DNA
    energy: float = 50.0
    age: int = 0
    generation: int = 1
    parent_id: int = -1
    symbol: str = "●"
    
    def __post_init__(self):
        self.max_age = int(80 + (4 - self.dna.genes['size']) * 20)
        self.energy = 40 + self.dna.genes['size'] * 10
    
    def metabolize(self):
        """Gasto energético por turno."""
        cost = (self.dna.genes['size'] ** 2) * self.dna.genes['metabolism'] * 0.4
        cost += self.dna.genes['speed'] * 0.2
        self.energy -= cost
        self.age += 1
    
    def can_reproduce(self):
        threshold = 60 + self.dna.genes['size'] * 15
        return (self.energy > threshold and 
                self.age > 3 and 
                random.random() < self.dna.genes['fertility'])
    
    def reproduce_cost(self):
        return 25 + self.dna.genes['size'] * 8
    
    def is_dead(self):
        return self.energy <= 0 or self.age >= self.max_age
    
    def move_towards(self, tx, ty, world_w, world_h):
        """Movimiento inteligente hacia objetivo."""
        dx = clamp(tx - self.x, -1, 1)
        dy = clamp(ty - self.y, -1, 1)
        speed = max(1, int(self.dna.genes['speed']))
        
        for _ in range(speed):
            if random.random() < 0.1:  # 10% de error de navegación
                dx, dy = random.choice([(-1,0),(1,0),(0,-1),(0,1),(0,0)])
            nx = clamp(self.x + dx, 0, world_w - 1)
            ny = clamp(self.y + dy, 0, world_h - 1)
            self.x, self.y = nx, ny

# ==================== MUNDO ====================

CLIMATES = {
    'normal':   {'food_spawn': 8, 'food_energy': 15, 'hazard': 0.0},
    'drought':  {'food_spawn': 2, 'food_energy': 10, 'hazard': 0.02},
    'paradise': {'food_spawn': 15, 'food_energy': 20, 'hazard': 0.0},
    'ice_age':  {'food_spawn': 4, 'food_energy': 12, 'hazard': 0.03},
    'toxic':    {'food_spawn': 6, 'food_energy': 8,  'hazard': 0.05},
}

class World:
    def __init__(self, width=50, height=24):
        self.w = width
        self.h = height
        self.creatures = []
        self.food = set()  # (x,y)
        self.climate = 'normal'
        self.turn = 0
        self.next_id = 1
        self.history = deque(maxlen=50)
        self.news = deque(maxlen=5)
        self.extinctions = set()
        
        # Semilla inicial
        for _ in range(12):
            self.spawn_creature(
                random.randint(0, width-1),
                random.randint(0, height-1)
            )
    
    def spawn_creature(self, x, y, parent=None, generation=1):
        if parent:
            dna = parent.dna.mutate()
            gen = parent.generation + 1
            pid = parent.id
        else:
            dna = DNA()
            gen = 1
            pid = -1
        
        c = Creature(
            id=self.next_id,
            x=x, y=y,
            dna=dna,
            generation=gen,
            parent_id=pid
        )
        self.next_id += 1
        self.creatures.append(c)
        return c
    
    def spawn_food(self):
        params = CLIMATES[self.climate]
        for _ in range(params['food_spawn']):
            self.food.add((
                random.randint(0, self.w - 1),
                random.randint(0, self.h - 1)
            ))
    
    def step(self):
        """Un turno de simulación."""
        params = CLIMATES[self.climate]
        self.turn += 1
        
        # Spawn comida
        self.spawn_food()
        
        # Peligros ambientales
        if random.random() < params['hazard']:
            victim = random.choice(self.creatures) if self.creatures else None
            if victim:
                victim.energy -= 30
                self.news.append(f"☠ {Color.RED}El clima hiere a criatura #{victim.id}{Color.RESET}")
        
        # Sobrepoblación
        if len(self.creatures) > 120:
            weakest = min(self.creatures, key=lambda c: c.energy)
            weakest.energy = 0
            self.news.append(f"⚠ Sobrepoblación mata a criatura #{weakest.id}")
        
        # Acción de criaturas
        new_creatures = []
        eaten_food = set()
        
        for c in self.creatures:
            # 1. Buscar comida
            target = self.find_nearest_food(c)
            if target:
                fx, fy = target
                dist = math.hypot(fx - c.x, fy - c.y)
                if dist <= c.dna.genes['sense']:
                    c.move_towards(fx, fy, self.w, self.h)
                    if (c.x, c.y) == (fx, fy):
                        c.energy += params['food_energy']
                        eaten_food.add(target)
                else:
                    # Movimiento aleatorio exploratorio
                    c.move_towards(
                        c.x + random.randint(-2, 2),
                        c.y + random.randint(-2, 2),
                        self.w, self.h
                    )
            else:
                c.move_towards(
                    c.x + random.randint(-2, 2),
                    c.y + random.randint(-2, 2),
                    self.w, self.h
                )
            
            # 2. Metabolismo
            c.metabolize()
            
            # 3. Reproducción
            if c.can_reproduce():
                cost = c.reproduce_cost()
                if c.energy >= cost + 10:
                    c.energy -= cost
                    child = self.spawn_creature(c.x, c.y, parent=c, generation=c.generation+1)
                    # Pequeño empujón para separarlos
                    child.x = clamp(child.x + random.choice([-1,0,1]), 0, self.w-1)
                    child.y = clamp(child.y + random.choice([-1,0,1]), 0, self.h-1)
                    new_creatures.append(child)
                    
                    # Noticias evolutivas
                    if child.dna.species_hash() != c.dna.species_hash():
                        self.news.append(
                            f"🧬 {Color.CYAN}Nueva especie en gen {child.generation}! "
                            f"(#{c.id} → #{child.id}){Color.RESET}"
                        )
        
        self.creatures.extend(new_creatures)
        self.food -= eaten_food
        
        # Eliminar muertos
        alive = []
        for c in self.creatures:
            if c.is_dead():
                if c.energy <= -20:  # Muerte violenta
                    pass
            else:
                alive.append(c)
        self.creatures = alive
        
        # Historial de stats
        if self.creatures:
            avg_genes = {k: sum(c.dna.genes[k] for c in self.creatures)/len(self.creatures) 
                        for k in GENE_RANGES}
        else:
            avg_genes = {k:0 for k in GENE_RANGES}
        
        species = defaultdict(int)
        for c in self.creatures:
            species[c.dna.species_hash()] += 1
        
        self.history.append({
            'turn': self.turn,
            'pop': len(self.creatures),
            'species': len(species),
            'genes': avg_genes
        })
    
    def find_nearest_food(self, creature):
        if not self.food:
            return None
        best = None
        best_d = float('inf')
        for f in self.food:
            d = math.hypot(f[0]-creature.x, f[1]-creature.y)
            if d < best_d:
                best_d = d
                best = f
        return best
    
    def render(self):
        """Dibuja el mundo en terminal."""
        clear()
        print(f"{Color.BOLD}{Color.CYAN}╔{'═'*(self.w+2)}╗{Color.RESET}")
        
        grid = [[' ' for _ in range(self.w)] for _ in range(self.h)]
        
        # Comida
        for fx, fy in self.food:
            if 0 <= fx < self.w and 0 <= fy < self.h:
                grid[fy][fx] = f"{Color.GREEN}·{Color.RESET}"
        
        # Criaturas (las más grandes se pintan encima)
        sorted_creatures = sorted(self.creatures, key=lambda c: c.dna.genes['size'])
        for c in sorted_creatures:
            if 0 <= c.x < self.w and 0 <= c.y < self.h:
                col = c.dna.phenotype_color()
                sym = "●" if c.dna.genes['size'] < 1.5 else "◉" if c.dna.genes['size'] < 2.5 else "▣"
                grid[c.y][c.x] = f"{col}{sym}{Color.RESET}"
        
        for row in grid:
            line = ''.join(row)
            print(f"{Color.CYAN}║ {Color.RESET}{line}{Color.CYAN} ║{Color.RESET}")
        
        print(f"{Color.BOLD}{Color.CYAN}╚{'═'*(self.w+2)}╝{Color.RESET}")
    
    def render_ui(self):
        """Panel de estadísticas."""
        print(f"\n{Color.BOLD}Turno: {self.turn}  |  Clima: {Color.YELLOW}{self.climate.upper()}{Color.RESET}")
        print(f"Población: {Color.GREEN}{len(self.creatures)}{Color.RESET}  |  "
              f"Especies distintas: {Color.MAGENTA}{len(set(c.dna.species_hash() for c in self.creatures))}{Color.RESET}")
        
        if self.creatures:
            avg = {k: sum(c.dna.genes[k] for c in self.creatures)/len(self.creatures) 
                   for k in GENE_RANGES}
            print(f"Genoma promedio: "
                  f"{Color.RED}Spd:{avg['speed']:.1f}{Color.RESET} "
                  f"{Color.YELLOW}Siz:{avg['size']:.1f}{Color.RESET} "
                  f"{Color.GREEN}Sen:{avg['sense']:.1f}{Color.RESET} "
                  f"{Color.CYAN}Met:{avg['metabolism']:.1f}{Color.RESET} "
                  f"{Color.MAGENTA}Fer:{avg['fertility']:.1f}{Color.RESET} "
                  f"{Color.BLUE}Mut:{avg['mut_rate']:.2f}{Color.RESET}")
            
            # Top criatura
            best = max(self.creatures, key=lambda c: c.energy)
            print(f"Criatura top: #{best.id} (Gen {best.generation}, Energía {best.energy:.0f})")
        
        if self.news:
            print(f"\n{Color.BOLD}─── ÚLTIMOS EVENTOS ───{Color.RESET}")
            for n in self.news:
                print(f"  {n}")
        
        print(f"\n{Color.DIM}Comandos: [Enter]=avanza | [1]=Plaga | [2]=Abundancia | [3]=Radiación | "
              f"[4]=Cataclismo | [5]=Clima | [6]=Introducir | [7]=Favorito | [8]=Estadísticas | [Q]=Salir{Color.RESET}")

# ==================== INTERVENCIONES DIVINAS ====================

class GodMode:
    def __init__(self, world):
        self.world = world
    
    def plague(self):
        if not self.world.creatures:
            return
        victims = random.sample(self.world.creatures, max(1, len(self.world.creatures)//3))
        for v in victims:
            v.energy -= 100
        self.world.news.append(f"☠ {Color.RED}¡PLAGA! {len(victims)} criaturas infectadas.{Color.RESET}")
    
    def abundance(self):
        for _ in range(40):
            self.world.food.add((
                random.randint(0, self.world.w-1),
                random.randint(0, self.world.h-1)
            ))
        self.world.news.append(f"🌿 {Color.GREEN}¡ABUNDANCIA! La tierra rebosa de nutrientes.{Color.RESET}")
    
    def radiation(self):
        for c in self.world.creatures:
            if random.random() < 0.5:
                c.dna = c.dna.mutate()
        self.world.news.append(f"☢ {Color.YELLOW}¡RADIACIÓN! Mutación masiva inducida.{Color.RESET}")
    
    def cataclysm(self):
        # Inundación desde abajo
        survivors = []
        for c in self.world.creatures:
            if c.y < self.world.h // 2:
                survivors.append(c)
            else:
                c.energy = 0
        self.world.creatures = [c for c in self.world.creatures if c.energy > 0]
        self.world.news.append(f"🌊 {Color.BLUE}¡CATACLISMO! Las aguas arrasan la mitad inferior.{Color.RESET}")
    
    def change_climate(self):
        climates = list(CLIMATES.keys())
        idx = climates.index(self.world.climate)
        self.world.climate = climates[(idx + 1) % len(climates)]
        self.world.news.append(f"🌍 {Color.CYAN}El clima cambia a: {self.world.climate.upper()}{Color.RESET}")
    
    def introduce(self):
        print(f"\n{Color.BOLD}Crear nueva criatura (Dios){Color.RESET}")
        try:
            x = int(input(f"X (0-{self.world.w-1}): "))
            y = int(input(f"Y (0-{self.world.h-1}): "))
            print("Genes por defecto: speed=2.0, size=1.5, sense=4.0, metabolism=1.0, fertility=0.5, mut_rate=0.2")
            custom = input("¿ADN personalizado? (s/N): ").lower() == 's'
            if custom:
                g = {}
                for k, (lo, hi) in GENE_RANGES.items():
                    g[k] = clamp(float(input(f"{k} ({lo}-{hi}): ")), lo, hi)
                dna = DNA(genes=g, lineage="divine")
            else:
                dna = DNA(lineage="divine")
            
            c = self.world.spawn_creature(x, y)
            c.dna = dna
            c.energy = 100
            self.world.news.append(f"✨ {Color.MAGENTA}¡Un dios ha sembrado vida en ({x},{y})!{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}Entrada inválida.{Color.RESET}")
            input("Enter para continuar...")
    
    def bless_best(self):
        if not self.world.creatures:
            return
        best = max(self.world.creatures, key=lambda c: c.energy)
        best.energy += 50
        best.dna.genes['fertility'] = clamp(best.dna.genes['fertility'] + 0.2, *GENE_RANGES['fertility'])
        self.world.news.append(f"👑 {Color.YELLOW}¡FAVORITO! La criatura #{best.id} ha sido bendecida.{Color.RESET}")
    
    def show_stats(self):
        if not self.world.history:
            print(f"{Color.YELLOW}Sin datos aún.{Color.RESET}")
            return
        
        print(f"\n{Color.BOLD}{Color.CYAN}══════ HISTORIAL EVOLUTIVO ══════{Color.RESET}")
        print(f"{'Turno':<8} {'Pob':<6} {'Esp':<5} {'Vel':<5} {'Tam':<5} {'Sent':<5}")
        print("-" * 40)
        for h in list(self.world.history)[-15:]:
            print(f"{h['turn']:<8} {h['pop']:<6} {h['species']:<5} "
                  f"{h['genes']['speed']:<5.1f} {h['genes']['size']:<5.1f} {h['genes']['sense']:<5.1f}")
        input(f"\n{Color.DIM}Presiona Enter para volver...{Color.RESET}")

# ==================== BUCLE PRINCIPAL ====================

def main():
    clear()
    print(f"""{Color.CYAN}{Color.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           E C O S I S T E M A   E V O L U T I V O            ║
    ║                                                               ║
    ║  Observa cómo la vida surge, compite, se adapta y muta.      ║
    ║  O no. Tú decides si ser un observador paciente...            ║
    ║  ...o un dios caprichoso.                                     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    {Color.RESET}""")
    input(f"{Color.DIM}Presiona Enter para sembrar la vida primordial...{Color.RESET}")
    
    world = World(width=52, height=22)
    god = GodMode(world)
    auto_mode = False
    
    while True:
        world.step()
        world.render()
        world.render_ui()
        
        if auto_mode:
            time.sleep(0.3)
            continue
        
        try:
            choice = input(f"\n{Color.BOLD}> {Color.RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        
        if choice == '':
            continue  # Siguiente turno
        elif choice == 'q':
            break
        elif choice == 'a':
            auto_mode = True
            print(f"{Color.YELLOW}Modo automático activado. Presiona Ctrl+C para detener.{Color.RESET}")
            time.sleep(1)
        elif choice == '1':
            god.plague()
        elif choice == '2':
            god.abundance()
        elif choice == '3':
            god.radiation()
        elif choice == '4':
            god.cataclysm()
        elif choice == '5':
            god.change_climate()
        elif choice == '6':
            god.introduce()
        elif choice == '7':
            god.bless_best()
        elif choice == '8':
            world.render()
            god.show_stats()
        else:
            print(f"{Color.RED}Comando no reconocido.{Color.RESET}")
            time.sleep(0.5)
    
    clear()
    print(f"{Color.GREEN}La simulación ha terminado. La vida... encuentra un camino.{Color.RESET}")

if __name__ == "__main__":
    main()
