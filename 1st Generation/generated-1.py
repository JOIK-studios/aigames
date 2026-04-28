#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TERMINAL HACKER: ORIGEN
Simulador de hacking por consola con mecánicas de rastreo, descifrado y comandos.
"""

import os
import sys
import time
import random
import string
import hashlib
from datetime import datetime

# ==================== CONFIGURACIÓN VISUAL ====================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewrite(text, delay=0.02, color=""):
    """Efecto de máquina de escribir."""
    if color:
        print(color, end="")
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    if color:
        print(Colors.END, end="")
    print()

def print_banner():
    banner = f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║     ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ║
║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗║
║        ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║║
║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║║
║        ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║║
║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝║
║                                                              ║
║              H A C K E R   ::   O R I G E N                  ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)

# ==================== SISTEMA DE RASTREO ====================

class TraceSystem:
    def __init__(self):
        self.level = 0  # 0-100
        self.active = False
        self.trace_speed = 5
    
    def increase(self, amount):
        self.level = min(100, self.level + amount)
        if self.level >= 100:
            self.trigger_bust()
    
    def decrease(self, amount):
        self.level = max(0, self.level - amount)
    
    def trigger_bust(self):
        clear()
        print(f"{Colors.RED}{Colors.BOLD}")
        print("""
    ╔═══════════════════════════════════════╗
    ║     ⚠  R A S T R E O  D E T E C T A D O  ⚠    ║
    ║                                       ║
    ║  Tu conexión ha sido comprometida.    ║
    ║  Los agentes de seguridad están en    ║
    ║  camino a tu ubicación.               ║
    ╚═══════════════════════════════════════╝
        """)
        print(f"{Colors.END}")
        typewrite(">>> SECUENCIA DE AUTODESTRUCCIÓN INICIADA...", 0.05, Colors.RED)
        time.sleep(1)
        typewrite(">>> BORRANDO ARCHIVOS...", 0.05, Colors.RED)
        time.sleep(1)
        typewrite(">>> CONEXIÓN TERMINADA.", 0.1, Colors.RED)
        sys.exit(0)
    
    def display(self):
        bar_length = 20
        filled = int((self.level / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        color = Colors.GREEN if self.level < 40 else Colors.YELLOW if self.level < 75 else Colors.RED
        print(f"\n{color}[RASTREO: |{bar}| {self.level}%]{Colors.END}")
        if self.level > 75:
            print(f"{Colors.RED}⚠ ALERTA: Rastreo crítico activo{Colors.END}")

# ==================== GENERADORES DE CONTENIDO ====================

def generate_ip():
    return f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def generate_password(length=8):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def generate_hex_phrase(word):
    return ' '.join(format(ord(c), '02x') for c in word)

def generate_binary_phrase(word):
    return ' '.join(format(ord(c), '08b') for c in word)

# ==================== MISIONES / NIVELES ====================

class Mission:
    def __init__(self, id, name, description, target_ip, security_level, password, clues, puzzle_type, puzzle_data, puzzle_answer):
        self.id = id
        self.name = name
        self.description = description
        self.target_ip = target_ip
        self.security_level = security_level
        self.password = password
        self.clues = clues
        self.puzzle_type = puzzle_type
        self.puzzle_data = puzzle_data
        self.puzzle_answer = puzzle_answer.lower()
        self.hacked = False
        self.connected = False
        self.files_downloaded = []
    
    def show_files(self):
        files = [
            "shadow_credentials.db", "financial_records.xlsx", "security_logs.txt",
            "employee_data.sql", "project_omega.pdf", "backdoor_access.exe",
            "encrypted_vault.key", "surveillance_feed.mp4", "admin_hashes.txt"
        ]
        return random.sample(files, 3)

MISSIONS = [
    Mission(
        id=1,
        name="Primeros Pasos",
        description="Un servidor de prueba en la red local. Tu iniciación.",
        target_ip="192.168.1.105",
        security_level=1,
        password="password123",
        clues=["El sysadmin nunca cambia los defaults.", "Prueba con 'password' + números comunes."],
        puzzle_type="none",
        puzzle_data="",
        puzzle_answer="password123"
    ),
    Mission(
        id=2,
        name="La Cafetería",
        description="Roba la lista de clientes frecuentes de CoffeeNet.",
        target_ip="203.45.112.8",
        security_level=2,
        password="mocha2024!",
        clues=["El dueño ama el café.", "Año actual + bebida favorita."],
        puzzle_type="caesar",
        puzzle_data=caesar_cipher("mocha2024", 3),
        puzzle_answer="mocha2024"
    ),
    Mission(
        id=3,
        name="Hexadecimal",
        description="Servidor universitario con datos de investigación.",
        target_ip="147.82.19.44",
        security_level=3,
        password="neutrino",
        clues=["La partícula fantasma.", "7 letras, empieza con n."],
        puzzle_type="hex",
        puzzle_data=generate_hex_phrase("neutrino"),
        puzzle_answer="neutrino"
    ),
    Mission(
        id=4,
        name="Código Binario",
        description="Instalación militar de baja seguridad. Datos de drones.",
        target_ip="55.231.78.12",
        security_level=4,
        password="eagle7",
        clues=["Ave de presa + número de la suerte del admin."],
        puzzle_type="binary",
        puzzle_data=generate_binary_phrase("eagle7"),
        puzzle_answer="eagle7"
    ),
    Mission(
        id=5,
        name="El Banco",
        description="El gran golpe. Sistema bancario central.",
        target_ip="10.0.0.1",
        security_level=5,
        password="f1n@nc13$",
        clues=["Leet speak de 'finances'.", "Reemplaza letras por números y símbolos."],
        puzzle_type="mixed",
        puzzle_data="73 79 73 74 65 6d 5f 72 6f 6f 74",
        puzzle_answer="system_root"
    )
]

# ==================== MOTOR DEL JUEGO ====================

class GameEngine:
    def __init__(self):
        self.trace = TraceSystem()
        self.current_mission_idx = 0
        self.inventory = []
        self.connected_to = None
        self.command_history = []
        self.player_name = "Anon"
        self.money = 0
        self.reputation = 0
    
    def intro(self):
        clear()
        print_banner()
        time.sleep(0.5)
        typewrite(f"{Colors.CYAN}Iniciando sistema seguro...", 0.03)
        time.sleep(0.5)
        typewrite(f"{Colors.GREEN}Conexión establecida mediante proxy #7X-99...", 0.03)
        time.sleep(0.3)
        print()
        typewrite(f"{Colors.YELLOW}Bienvenido, operativo. No hay nombres aquí, solo código.", 0.02)
        typewrite(f"{Colors.YELLOW}Tu objetivo: infiltrar sistemas, extraer datos, no dejar rastros.", 0.02)
        typewrite(f"{Colors.YELLOW}Cada error aumenta el rastreo. Si llega al 100%, estás terminado.", 0.02)
        print()
        input(f"{Colors.CYAN}[PRESIONA ENTER PARA INICIAR]{Colors.END}")
    
    def help_menu(self):
        help_text = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    COMANDOS DISPONIBLES                       ║
╠══════════════════════════════════════════════════════════════╣
║  {Colors.GREEN}scan{Colors.CYAN}              - Escanear redes cercanas                ║
║  {Colors.GREEN}connect <ip>{Colors.CYAN}      - Conectar a un objetivo                   ║
║  {Colors.GREEN}disconnect{Colors.CYAN}        - Cerrar conexión actual                   ║
║  {Colors.GREEN}analyze{Colors.CYAN}           - Analizar seguridad del sistema             ║
║  {Colors.GREEN}clues{Colors.CYAN}             - Mostrar pistas disponibles                 ║
║  {Colors.GREEN}brute <password>{Colors.CYAN}  - Intentar fuerza bruta (¡alto riesgo!)      ║
║  {Colors.GREEN}decrypt{Colors.CYAN}           - Resolver puzzle de acceso                  ║
║  {Colors.GREEN}hack{Colors.CYAN}              - Ejecutar exploit una vez conectado         ║
║  {Colors.GREEN}download{Colors.CYAN}          - Descargar archivos del sistema             ║
║  {Colors.GREEN}clear{Colors.CYAN}             - Limpiar pantalla                           ║
║  {Colors.GREEN}status{Colors.CYAN}            - Ver estado del rastreo                     ║
║  {Colors.GREEN}missions{Colors.CYAN}          - Listar misiones disponibles                ║
║  {Colors.GREEN}exit{Colors.CYAN}              - Salir del sistema                          ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
"""
        print(help_text)
    
    def get_prompt(self):
        if self.connected_to:
            return f"{Colors.RED}[{self.connected_to}]{Colors.END} {Colors.GREEN}root@ghost:{Colors.END}~$ "
        return f"{Colors.GREEN}root@ghost:{Colors.END}~$ "
    
    def cmd_scan(self):
        typewrite(f"{Colors.CYAN}Iniciando escaneo de red...{Colors.END}", 0.02)
        time.sleep(1)
        print(f"\n{Colors.YELLOW}Objetivos detectados:{Colors.END}")
        for i, m in enumerate(MISSIONS):
            status = f"{Colors.GREEN}[HACKEADO]{Colors.END}" if m.hacked else f"{Colors.RED}[ACTIVO]{Colors.END}"
            print(f"  {i+1}. {m.target_ip} - {m.name} {status}")
        print()
        self.trace.increase(2)
    
    def cmd_connect(self, args):
        if not args:
            print(f"{Colors.RED}Uso: connect <ip>{Colors.END}")
            return
        
        ip = args[0]
        mission = None
        for m in MISSIONS:
            if m.target_ip == ip:
                mission = m
                break
        
        if not mission:
            print(f"{Colors.RED}Error: IP no encontrada en la red.{Colors.END}")
            self.trace.increase(5)
            return
        
        if mission.hacked:
            print(f"{Colors.YELLOW}Ya has comprometido este sistema.{Colors.END}")
            return
        
        typewrite(f"{Colors.CYAN}Estableciendo conexión con {ip}...{Colors.END}", 0.02)
        time.sleep(1.5)
        
        # Simulación de firewall
        dots = random.randint(3, 6)
        for _ in range(dots):
            print(f"{Colors.YELLOW}.", end="", flush=True)
            time.sleep(0.4)
        print(Colors.END)
        
        if random.random() < 0.1:  # 10% de fallo aleatorio
            print(f"{Colors.RED}Conexión rechazada por firewall.{Colors.END}")
            self.trace.increase(8)
            return
        
        self.connected_to = ip
        mission.connected = True
        print(f"{Colors.GREEN}✓ Conexión establecida con {ip}{Colors.END}")
        print(f"{Colors.CYAN}Nivel de seguridad: {'★' * mission.security_level}{Colors.END}")
        self.trace.increase(3)
    
    def cmd_disconnect(self):
        if not self.connected_to:
            print(f"{Colors.YELLOW}No hay conexión activa.{Colors.END}")
            return
        print(f"{Colors.CYAN}Cerrando conexión segura...{Colors.END}")
        time.sleep(0.5)
        self.connected_to = None
        self.trace.decrease(5)
        print(f"{Colors.GREEN}✓ Desconectado.{Colors.END}")
    
    def cmd_analyze(self):
        if not self.connected_to:
            print(f"{Colors.RED}Error: No estás conectado a ningún sistema.{Colors.END}")
            return
        
        mission = self.get_current_mission()
        typewrite(f"{Colors.CYAN}Analizando vectores de ataque...{Colors.END}", 0.02)
        time.sleep(1)
        print(f"\n{Colors.YELLOW}Resultados del análisis:{Colors.END}")
        print(f"  - Firewall: Activo (Nivel {mission.security_level})")
        print(f"  - Puertos abiertos: 22, 80, 443, 8080")
        print(f"  - Sistema operativo: Linux 5.15.0-custom")
        print(f"  - Vulnerabilidad detectada: Buffer overflow en servicio SSH")
        print(f"  - Método recomendado: Fuerza bruta controlada o descifrado de pista")
        print()
        self.trace.increase(4)
    
    def cmd_clues(self):
        if not self.connected_to:
            print(f"{Colors.RED}Error: Conéctate primero a un objetivo.{Colors.END}")
            return
        
        mission = self.get_current_mission()
        print(f"\n{Colors.CYAN}═══ PISTAS DEL SISTEMA ═══{Colors.END}")
        for i, clue in enumerate(mission.clues, 1):
            print(f"  {Colors.YELLOW}{i}.{Colors.END} {clue}")
        print()
    
    def cmd_decrypt(self):
        if not self.connected_to:
            print(f"{Colors.RED}Error: No hay conexión activa.{Colors.END}")
            return
        
        mission = self.get_current_mission()
        print(f"\n{Colors.CYAN}═══ PUZZLE DE ACCESO ═══{Colors.END}")
        
        if mission.puzzle_type == "caesar":
            print(f"{Colors.YELLOW}Texto cifrado (César +3):{Colors.END} {mission.puzzle_data}")
            print(f"{Colors.CYAN}Pista: Cada letra se ha desplazado 3 posiciones en el alfabeto.{Colors.END}")
        elif mission.puzzle_type == "hex":
            print(f"{Colors.YELLOW}Texto en hexadecimal:{Colors.END} {mission.puzzle_data}")
            print(f"{Colors.CYAN}Pista: Convierte cada par hex a su valor ASCII.{Colors.END}")
        elif mission.puzzle_type == "binary":
            print(f"{Colors.YELLOW}Texto en binario:{Colors.END} {mission.puzzle_data}")
            print(f"{Colors.CYAN}Pista: Cada grupo de 8 bits es un carácter ASCII.{Colors.END}")
        elif mission.puzzle_type == "mixed":
            print(f"{Colors.YELLOW}Datos codificados:{Colors.END} {mission.puzzle_data}")
            print(f"{Colors.CYAN}Pista: Hex → ASCII. Es el nombre de una cuenta.{Colors.END}")
        else:
            print(f"{Colors.GREEN}Este sistema no requiere puzzle. Usa 'brute'.{Colors.END}")
            return
        
        answer = input(f"\n{Colors.GREEN}Introduce la contraseña descifrada: {Colors.END}").strip().lower()
        
        if answer == mission.puzzle_answer:
            print(f"{Colors.GREEN}✓ ¡Descifrado correcto! Acceso concedido.{Colors.END}")
            mission.hacked = True
            self.reputation += 10 * mission.security_level
            self.complete_mission(mission)
        else:
            print(f"{Colors.RED}✗ Contraseña incorrecta.{Colors.END}")
            self.trace.increase(10)
    
    def cmd_brute(self, args):
        if not self.connected_to:
            print(f"{Colors.RED}Error: Conéctate primero.{Colors.END}")
            return
        
        mission = self.get_current_mission()
        guess = args[0] if args else ""
        
        if not guess:
            print(f"{Colors.YELLOW}Uso: brute <password>{Colors.END}")
            return
        
        typewrite(f"{Colors.CYAN}Iniciando ataque de fuerza bruta...{Colors.END}", 0.02)
        
        # Simulación visual
        for i in range(random.randint(5, 15)):
            fake_pw = generate_password(random.randint(6, 10))
            print(f"  Probando: {fake_pw} ... {Colors.RED}FAIL{Colors.END}")
            time.sleep(0.1)
        
        if guess.lower() == mission.password.lower():
            print(f"  Probando: {guess} ... {Colors.GREEN}SUCCESS{Colors.END}")
            print(f"{Colors.GREEN}✓ ¡Acceso concedido por fuerza bruta!{Colors.END}")
            mission.hacked = True
            self.reputation += 5 * mission.security_level
            self.trace.increase(15)  # Más riesgo
            self.complete_mission(mission)
        else:
            print(f"  Probando: {guess} ... {Colors.RED}FAIL{Colors.END}")
            print(f"{Colors.RED}✗ Contraseña incorrecta.{Colors.END}")
            self.trace.increase(20)  # Penalización alta por fuerza bruta fallida
    
    def cmd_hack(self):
        if not self.connected_to:
            print(f"{Colors.RED}Error: No estás conectado.{Colors.END}")
            return
        
        mission = self.get_current_mission()
        if mission.hacked:
            print(f"{Colors.YELLOW}El sistema ya está comprometido.{Colors.END}")
            return
        
        # Hack requiere que se haya resuelto el puzzle o brute force
        print(f"{Colors.RED}Necesitas descifrar la contraseña primero ('decrypt') o usar fuerza bruta ('brute').{Colors.END}")
    
    def cmd_download(self):
        if not self.connected_to:
            print(f"{Colors.RED}Error: Conéctate primero.{Colors.END}")
            return
        
        mission = self.get_current_mission()
        if not mission.hacked:
            print(f"{Colors.RED}Error: El sistema no ha sido comprometido aún.{Colors.END}")
            return
        
        files = mission.show_files()
        print(f"\n{Colors.CYAN}═══ ARCHIVOS DISPONIBLES ═══{Colors.END}")
        for i, f in enumerate(files, 1):
            print(f"  {Colors.GREEN}{i}.{Colors.END} {f}")
        
        choice = input(f"\n{Colors.YELLOW}Selecciona archivo para descargar (1-3): {Colors.END}").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                file = files[idx]
                typewrite(f"{Colors.CYAN}Descargando {file}...{Colors.END}", 0.02)
                time.sleep(1)
                size = random.randint(10, 500)
                print(f"{Colors.GREEN}✓ Descarga completa: {file} ({size} MB){Colors.END}")
                mission.files_downloaded.append(file)
                self.money += random.randint(100, 1000)
                self.trace.increase(5)
            else:
                print(f"{Colors.RED}Selección inválida.{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Entrada inválida.{Colors.END}")
    
    def cmd_missions(self):
        print(f"\n{Colors.CYAN}═══ REGISTRO DE MISIONES ═══{Colors.END}")
        for m in MISSIONS:
            status = f"{Colors.GREEN}[COMPLETADA]{Colors.END}" if m.hacked else f"{Colors.RED}[PENDIENTE]{Colors.END}"
            files = f" | Archivos: {len(m.files_downloaded)}" if m.hacked else ""
            print(f"  {m.id}. {m.name} {status}{files}")
        print(f"\n{Colors.YELLOW}Reputación: {self.reputation} | Fondos: ${self.money}{Colors.END}\n")
    
    def get_current_mission(self):
        for m in MISSIONS:
            if m.target_ip == self.connected_to:
                return m
        return None
    
    def complete_mission(self, mission):
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("╔═══════════════════════════════════════╗")
        print("║     S I S T E M A   C O M P R O M E T I D O    ║")
        print("╚═══════════════════════════════════════╝")
        print(f"{Colors.END}")
        typewrite(f"{Colors.CYAN}Obteniendo acceso root...{Colors.END}", 0.03)
        typewrite(f"{Colors.CYAN}Instalando puerta trasera...{Colors.END}", 0.03)
        typewrite(f"{Colors.GREEN}✓ Misión '{mission.name}' completada.{Colors.END}", 0.03)
        print()
        
        # Bonus por bajo rastreo
        if self.trace.level < 30:
            bonus = 500
            self.money += bonus
            print(f"{Colors.GREEN}Bonus sigilo: +${bonus}{Colors.END}")
        
        self.check_victory()
    
    def check_victory(self):
        if all(m.hacked for m in MISSIONS):
            time.sleep(1)
            clear()
            print(f"{Colors.GREEN}{Colors.BOLD}")
            print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           F E L I C I D A D E S,   O P E R A T I V O          ║
    ║                                                               ║
    ║     Has comprometido todos los sistemas objetivo.            ║
    ║     Tu nombre (o falta de él) será recordado en la red.      ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
            """)
            print(f"{Colors.END}")
            print(f"{Colors.CYAN}Estadísticas finales:{Colors.END}")
            print(f"  Reputación: {self.reputation}")
            print(f"  Fondos acumulados: ${self.money}")
            print(f"  Nivel de rastreo final: {self.trace.level}%")
            sys.exit(0)
    
    def run(self):
        self.intro()
        clear()
        print_banner()
        self.help_menu()
        
        while True:
            self.trace.display()
            try:
                cmd_line = input(self.get_prompt()).strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Colors.RED}Saliendo del sistema...{Colors.END}")
                break
            
            if not cmd_line:
                continue
            
            self.command_history.append(cmd_line)
            parts = cmd_line.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd == "help":
                self.help_menu()
            elif cmd == "clear":
                clear()
                print_banner()
            elif cmd == "scan":
                self.cmd_scan()
            elif cmd == "connect":
                self.cmd_connect(args)
            elif cmd == "disconnect":
                self.cmd_disconnect()
            elif cmd == "analyze":
                self.cmd_analyze()
            elif cmd == "clues":
                self.cmd_clues()
            elif cmd == "decrypt":
                self.cmd_decrypt()
            elif cmd == "brute":
                self.cmd_brute(args)
            elif cmd == "hack":
                self.cmd_hack()
            elif cmd == "download":
                self.cmd_download()
            elif cmd == "status":
                self.trace.display()
            elif cmd == "missions":
                self.cmd_missions()
            elif cmd == "exit":
                typewrite(f"{Colors.YELLOW}Cerrando sesión segura...{Colors.END}", 0.03)
                break
            else:
                print(f"{Colors.RED}Comando no reconocido: '{cmd}'. Escribe 'help' para ver opciones.{Colors.END}")
                self.trace.increase(1)  # Pequeña penalización por comandos inválidos

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        print(f"{Colors.RED}Error crítico del sistema: {e}{Colors.END}")
