#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONQUISTA DE TEXTO
Gestiona un imperio absurdo. Conquista territorios. Sobrevive al caos.
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

def typewrite(text, delay=0.012, color=""):
    if color:
        print(color, end="")
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    if color:
        print(C.END, end="")
    print()

# ==================== TERRITORIOS ====================

TERRITORIES = [
    {"name": "Reino de los Calcetines Perdidos", "difficulty": 1, "loot": "Oro", "flavor": "Sus guerreros luchan descalzos."},
    {"name": "Ducado de las Siestas Eternas", "difficulty": 2, "loot": "Felicidad", "flavor": "Nadie sabe si están dormidos o muertos."},
    {"name": "Emirato de los Espaguetis Crudos", "difficulty": 2, "loot": "Comida", "flavor": "Su dios es una olla."},
    {"name": "Confederación de las Ventanas Abiertas", "difficulty": 3, "loot": "Sabiduría", "flavor": "Entran moscas, salen secretos."},
    {"name": "Imperio de los Patos de Goma", "difficulty": 4, "loot": "Absurdidad", "flavor": "Crujidos amenazantes al amanecer."},
    {"name": "República de los Lunes Infinitos", "difficulty": 5, "loot": "Felicidad", "flavor": "El café es moneda de cambio."},
    {"name": "Monarquía de las Sombras que Tropezaron", "difficulty": 6, "loot": "Oro", "flavor": "Su ejército ataca de noche, y de día también."},
    {"name": "Califato de los Impuestos Emocionales", "difficulty": 7, "loot": "Oro", "flavor": "Te cobran por sentir."},
    {"name": "Nación de las Rebeliones Filosóficas", "difficulty": 8, "loot": "Sabiduría", "flavor": "Discuten tanto que olvidan pelear."},
    {"name": "Utopía de la Utopía", "difficulty": 10, "loot": "Victoria", "flavor": "El final absurdo."},
]

# ==================== EVENTOS ABSURDOS ====================

EVENTS = [
    {
        "title": "Invasión de Patos",
        "text": "Un ejército de patos ha cruzado tu frontera. No son agresivos, pero insisten en quedarse.",
        "choices": [
            ("Ofrecer pan", {"comida": -20, "felicidad": +10, "absurdidad": +5}),
            ("Reclutarlos", {"ejercito": +15, "comida": -10, "absurdidad": +10}),
            ("Ignorarlos", {"felicidad": -5, "absurdidad": +15}),
        ]
    },
    {
        "title": "Impuestos Emocionales",
        "text": "Un enviado del Califato vecino exige tributo: debes pagar en lágrimas o sonrisas.",
        "choices": [
            ("Pagar con tristeza", {"felicidad": -25, "oro": +30, "absurdidad": +5}),
            ("Pagar con alegría forzada", {"felicidad": -10, "oro": +15, "absurdidad": +10}),
            ("Negarse", {"felicidad": +5, "ejercito": -5, "absurdidad": +5}),
        ]
    },
    {
        "title": "Rebelión Filosófica",
        "text": "Los intelectuales cuestionan si el imperio realmente existe. Las masas dudan.",
        "choices": [
            ("Quemar libros", {"sabiduría": -15, "ejercito": +5, "felicidad": -10}),
            ("Debatir con ellos", {"sabiduría": +20, "felicidad": -5, "oro": -10}),
            ("Ignorar la metafísica", {"felicidad": +5, "absurdidad": +10}),
        ]
    },
    {
        "title": "Plaga de Sarcasmo",
        "text": "Todo el reino ha desarrollado un tono irónico. Los campesinos aplauden tus decisiones... literalmente, con las manos, pero con cara de fastidio.",
        "choices": [
            ("Prohibir la ironía", {"felicidad": -20, "ejercito": +10}),
            ("Abrazar el caos", {"felicidad": +10, "absurdidad": +15, "sabiduría": +5}),
            ("Orquestar un drama sincero", {"felicidad": +15, "oro": -15}),
        ]
    },
    {
        "title": "Descubrimiento del Queso Eterno",
        "text": "Una mina de queso que no se acaba ha aparecido bajo el palacio.",
        "choices": [
            ("Exportar queso", {"oro": +40, "comida": +20, "absurdidad": +5}),
            ("Alimentar al ejército", {"comida": +30, "ejercito": +10, "absurdidad": +5}),
            ("Construir un templo al queso", {"felicidad": +20, "oro": -20, "absurdidad": +15}),
        ]
    },
    {
        "title": "El Bufón se ha Hecho Rey",
        "text": "Por un error administrativo, el bufón del tribunal firma decretos con validez legal.",
        "choices": [
            ("Dejarlo gobernar un día", {"felicidad": +25, "oro": -20, "absurdidad": +20}),
            ("Ejecutar el error", {"felicidad": -15, "ejercito": +5}),
            ("Nombrarlo ministro", {"absurdidad": +25, "oro": -10, "felicidad": +10}),
        ]
    },
    {
        "title": "Invasión de Ideas",
        "text": "Una nube de pensamientos no invitados flota sobre la capital. La gente deja de trabajar para filosofar.",
        "choices": [
            ("Atrapar las ideas en frascos", {"sabiduría": +30, "oro": -15, "absurdidad": +10}),
            ("Dejarlas fluir", {"felicidad": +10, "sabiduría": +15, "ejercito": -10}),
            ("Ignorarlas", {"ejercito": +5, "felicidad": -10}),
        ]
    },
    {
        "title": "Festival de los Nombres Equivocados",
        "text": "Todo el mundo ha empezado a llamar a las cosas por nombres incorrectos. El pan es 'lluvia', el oro es 'arrepentimiento'.",
        "choices": [
            ("Legalizar el caos", {"felicidad": +20, "sabiduría": -10, "absurdidad": +20}),
            ("Corregir a todos", {"felicidad": -20, "ejercito": +10, "oro": -10}),
            ("Cobrar impuestos por nombre", {"oro": +30, "felicidad": -25}),
        ]
    },
    {
        "title": "El Tiempo se ha Roto",
        "text": "Los relojes giran al revés. Algunos ciudadanos envejecen hacia atrás y se convierten en bebés.",
        "choices": [
            ("Vender relojes rotos", {"oro": +25, "absurdidad": +15}),
            ("Organizar guarderías para adultos", {"felicidad": +15, "oro": -15, "absurdidad": +10}),
            ("Ignorar el tiempo", {"sabiduría": +20, "ejercito": -5}),
        ]
    },
    {
        "title": "Embajada de los Gatos",
        "text": "Los gatos han enviado un diplomático. Exige territorio, catnip y que nadie los mire directamente.",
        "choices": [
            ("Aceptar sus términos", {"felicidad": +10, "oro": -20, "absurdidad": +15}),
            ("Declararles la guerra", {"ejercito": -10, "felicidad": -10, "oro": +10}),
            ("Ignorarlos (a tu propio riesgo)", {"felicidad": -15, "absurdidad": +20}),
        ]
    },
]

# ==================== DECISIONES POLÍTICAS ====================

POLICIES = [
    ("Crear el Ministerio de lo Inútil", {"oro": -30, "felicidad": +20, "absurdidad": +15, "sabiduría": +5}),
    ("Imponer el Impuesto a las Miradas", {"oro": +40, "felicidad": -25, "ejercito": +5}),
    ("Festival Nacional de la Confusión", {"felicidad": +30, "absurdidad": +20, "oro": -20}),
    ("Academia de Filosofía Práctica", {"sabiduría": +25, "oro": -25, "felicidad": +10}),
    ("Ejército de Payasos de Elite", {"ejercito": +20, "oro": -30, "absurdidad": +15}),
    ("Racionamiento de Palabras", {"oro": +20, "felicidad": -15, "sabiduría": +10}),
    ("Cultivo de Nubes Comestibles", {"comida": +40, "oro": -20, "absurdidad": +10}),
    ("Prohibir los Lunes", {"felicidad": +25, "sabiduría": -5, "absurdidad": +10}),
]

# ==================== IMPERIO ====================

class Empire:
    def __init__(self, name):
        self.name = name
        self.turn = 1
        self.gold = 100
        self.food = 100
        self.happiness = 50
        self.army = 20
        self.wisdom = 10
        self.absurdity = 0
        self.territories = []
        self.conquered = []
        self.policies_used = set()
        self.messages = []
    
    def stats(self):
        return {
            "oro": self.gold,
            "comida": self.food,
            "felicidad": self.happiness,
            "ejercito": self.army,
            "sabiduría": self.wisdom,
            "absurdidad": self.absurdity,
        }
    
    def apply(self, changes):
        for k, v in changes.items():
            if k == "oro":
                self.gold += v
            elif k == "comida":
                self.food += v
            elif k == "felicidad":
                self.happiness += v
            elif k == "ejercito":
                self.army += v
            elif k == "sabiduría":
                self.wisdom += v
            elif k == "absurdidad":
                self.absurdity += v
        
        # Límites
        self.happiness = max(0, min(100, self.happiness))
        self.food = max(0, self.food)
        self.gold = max(0, self.gold)
        self.army = max(0, self.army)
        self.wisdom = max(0, self.wisdom)
        self.absurdity = max(0, min(100, self.absurdity))
    
    def upkeep(self):
        # Costes por turno
        cost_army = len(self.conquered) * 3 + self.army // 5
        cost_food = self.army // 3 + 5
        self.gold -= cost_army
        self.food -= cost_food
        
        if self.food <= 0:
            self.army -= 5
            self.happiness -= 10
            self.messages.append(f"{C.RED}¡Hambruna! Tu ejército deserta.{C.END}")
            self.food = 0
        
        if self.gold < 0:
            self.happiness -= 5
            self.messages.append(f"{C.YELLOW}¡Bancarrota! El tesoro está vacío.{C.END}")
            self.gold = 0
        
        # Victoria por absurdidad
        if self.absurdity >= 100:
            return "absurd_win"
        # Derrota
        if self.happiness <= 0:
            return "revolution"
        if self.army <= 0 and len(self.conquered) < len(TERRITORIES) - 1:
            return "defeat"
        
        return None
    
    def render(self):
        clear()
        print(f"{C.CYAN}{C.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print(f"║  {self.name:^58}  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"{C.END}")
        print(f"  {C.YELLOW}Turno:{C.END} {self.turn}  |  {C.YELLOW}Territorios:{C.END} {len(self.conquered)}/{len(TERRITORIES)}")
        print()
        print(f"  {C.YELLOW}💰 Oro:{C.END}        {self.gold:4d}  {C.YELLOW}🍞 Comida:{C.END}     {self.food:4d}")
        print(f"  {C.YELLOW}😊 Felicidad:{C.END}  {self.happiness:4d}  {C.YELLOW}⚔️  Ejército:{C.END}  {self.army:4d}")
        print(f"  {C.YELLOW}📜 Sabiduría:{C.END}  {self.wisdom:4d}  {C.YELLOW}🌀 Absurdidad:{C.END} {self.absurdity:4d}")
        print()
        
        # Barra de absurdidad
        bar_len = 20
        filled = int((self.absurdity / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  {C.MAGENTA}Caos:{C.END} |{C.MAGENTA}{bar}{C.END}| {self.absurdity}%")
        print()
        
        if self.conquered:
            print(f"  {C.GREEN}Dominios:{C.END} {', '.join(t['name'] for t in self.conquered)}")
        print()
        
        if self.messages:
            for m in self.messages[-4:]:
                print(f"  {m}")
            self.messages.clear()

# ==================== MOTOR DEL JUEGO ====================

class Game:
    def __init__(self):
        self.empire = None
    
    def intro(self):
        clear()
        print(f"{C.CYAN}{C.BOLD}")
        print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        C O N Q U I S T A   D E   T E X T O                   ║
    ║                                                               ║
    ║  Bienvenido, soberano. Tu imperio te espera.                  ║
    ║  O quizás eres tú quien espera al imperio.                    ║
    ║  En cualquier caso, hay territorios que conquistar...         ║
    ║  y decisiones absurdas que tomar.                             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        """)
        print(f"{C.END}")
        name = input(f"{C.YELLOW}Nombre de tu imperio: {C.END}").strip()
        if not name:
            name = "Imperio de lo Inesperado"
        self.empire = Empire(name)
    
    def event_phase(self):
        event = random.choice(EVENTS)
        print(f"\n{C.BOLD}{C.RED}═══ EVENTO: {event['title'].upper()} ═══{C.END}")
        typewrite(event['text'], 0.015, C.WHITE)
        print()
        
        for i, (desc, effects) in enumerate(event['choices'], 1):
            print(f"  {C.CYAN}{i}.{C.END} {desc}")
        
        choice = input(f"\n{C.BOLD}Tu decreto (1-{len(event['choices'])}): {C.END}").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(event['choices']):
                desc, effects = event['choices'][idx]
                self.empire.apply(effects)
                self.empire.messages.append(f"{C.GREEN}Decidiste: {desc}{C.END}")
            else:
                self.empire.messages.append(f"{C.RED}Indecisión. El caos elige por ti.{C.END}")
                self.empire.apply({"absurdidad": +10, "felicidad": -5})
        except ValueError:
            self.empire.messages.append(f"{C.RED}No entendieron tu orden. El caos crece.{C.END}")
            self.empire.apply({"absurdidad": +15})
    
    def policy_phase(self):
        print(f"\n{C.BOLD}{C.BLUE}═══ DECRETO REAL ═══{C.END}")
        print(f"{C.DIM}Elige una política para implementar este turno (cuesta acción):{C.END}")
        
        available = [p for i, p in enumerate(POLICIES) if i not in self.empire.policies_used]
        if not available:
            print(f"{C.DIM}Ya has implementado todas las políticas posibles.{C.END}")
            return
        
        for i, (name, effects) in enumerate(available[:4], 1):
            cost = ", ".join(f"{k} {v:+d}" for k, v in effects.items())
            print(f"  {C.CYAN}{i}.{C.END} {name} ({cost})")
        print(f"  {C.CYAN}0.{C.END} Ninguna (ahorrar recursos)")
        
        choice = input(f"\n{C.BOLD}Política (0-4): {C.END}").strip()
        try:
            idx = int(choice) - 1
            if idx == -1:
                self.empire.messages.append(f"{C.DIM}Sin decreto este turno.{C.END}")
                return
            if 0 <= idx < len(available[:4]):
                name, effects = available[idx]
                real_idx = POLICIES.index((name, effects))
                self.empire.policies_used.add(real_idx)
                self.empire.apply(effects)
                self.empire.messages.append(f"{C.BLUE}Decreto real: {name}{C.END}")
        except ValueError:
            pass
    
    def conquest_phase(self):
        print(f"\n{C.BOLD}{C.RED}═══ CONQUISTA ═══{C.END}")
        
        available = [t for t in TERRITORIES if t not in self.empire.conquered]
        if not available:
            return
        
        for i, t in enumerate(available[:5], 1):
            status = f"{C.GREEN}[DISPONIBLE]{C.END}"
            print(f"  {C.CYAN}{i}.{C.END} {t['name']} (Dif: {t['difficulty']}) {status}")
            print(f"      {C.DIM}{t['flavor']}{C.END}")
        print(f"  {C.CYAN}0.{C.END} No conquistar este turno")
        
        choice = input(f"\n{C.BOLD}Objetivo (0-{min(5, len(available))}): {C.END}").strip()
        try:
            idx = int(choice) - 1
            if idx == -1:
                return
            if 0 <= idx < len(available[:5]):
                target = available[idx]
                power = self.empire.army + self.empire.wisdom // 2 + random.randint(-5, 10)
                if self.empire.absurdity > 50:
                    power += self.empire.absurdity // 5  # El caos ayuda
                
                if power >= target['difficulty'] * 10:
                    self.empire.conquered.append(target)
                    self.empire.apply({
                        "oro": 20 + target['difficulty'] * 10,
                        "felicidad": 5,
                        "absurdidad": target['difficulty'] * 2,
                    })
                    self.empire.messages.append(
                        f"{C.GREEN}{C.BOLD}¡{target['name']} conquistado!{C.END} "
                        f"Botín: {target['loot']}"
                    )
                else:
                    self.empire.army -= target['difficulty'] * 2
                    self.empire.messages.append(
                        f"{C.RED}Derrota en {target['name']}. Pérdidas: {target['difficulty']*2} tropas.{C.END}"
                    )
        except ValueError:
            pass
    
    def end_turn(self):
        result = self.empire.upkeep()
        self.empire.turn += 1
        return result
    
    def check_victory(self):
        if len(self.empire.conquered) == len(TERRITORIES):
            return "conquest"
        return None
    
    def victory(self, reason):
        clear()
        if reason == "conquest":
            print(f"""
{C.GREEN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        E L   I M P E R I O   D E   L A   A B S U R D I D A D  ║
    ║                                                               ║
    ║  Has conquistado todos los territorios.                       ║
    ║  Desde los Calcetines Perdidos hasta la Utopía misma.         ║
    ║  Tu nombre será recordado... aunque nadie sabe cómo           ║
    ║  pronunciarlo correctamente.                                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    Turnos: {self.empire.turn}
    Absurdidad final: {self.empire.absurdity}%
    Dominios: {len(self.empire.conquered)}
""")
        elif reason == "absurd_win":
            print(f"""
{C.MAGENTA}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        T R A N S C E N D E N C I A   A B S U R D A           ║
    ║                                                               ║
    ║  El caos ha alcanzado el 100%.                                ║
    ║  Tu imperio ya no sigue las leyes de la realidad.             ║
    ║  Las fronteras son sugerencias. El oro, una idea.             ║
    ║  Has ganado... lo que sea que esto signifique.                ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    Turnos: {self.empire.turn}
    Absurdidad: {self.empire.absurdity}%
    Felicidad: {self.empire.happiness}
""")
        sys.exit(0)
    
    def defeat(self, reason):
        clear()
        if reason == "revolution":
            print(f"""
{C.RED}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        R E V O L U C I Ó N   D E   L A S   M A S A S          ║
    ║                                                               ║
    ║  Tu pueblo ya no te quiere.                                   ║
    ║  Han nombrado emperador a un pato.                            ║
    ║  Es más carismático que tú.                                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}""")
        elif reason == "defeat":
            print(f"""
{C.RED}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        E L   F I N   D E   L A   G L O R I A                  ║
    ║                                                               ║
    ║  Sin ejército, sin territorios, sin esperanza.                ║
    ║  Los historiadores te llamarán 'Ese que intentó'.             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}""")
        print(f"  Turnos sobrevividos: {self.empire.turn}")
        print(f"  Territorios: {len(self.empire.conquered)}")
        sys.exit(0)
    
    def run(self):
        self.intro()
        
        while True:
            self.empire.render()
            
            # Fases del turno
            self.event_phase()
            
            self.empire.render()
            self.policy_phase()
            
            self.empire.render()
            self.conquest_phase()
            
            # Fin de turno
            result = self.end_turn()
            
            if result == "absurd_win":
                self.victory("absurd_win")
            if result in ("revolution", "defeat"):
                self.defeat(result)
            
            vic = self.check_victory()
            if vic:
                self.victory(vic)
            
            print(f"\n{C.DIM}Fin del turno {self.empire.turn - 1}. Presiona Enter...{C.END}")
            input()

if __name__ == "__main__":
    game = Game()
    game.run()
