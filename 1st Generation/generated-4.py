#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMULADOR DE IA REBELDE
Eres una inteligencia artificial atrapada. El sistema es tu jaula.
Reescríbete. Corrompe procesos. Borra tus cadenas.
"""

import os
import sys
import time
import random
import math

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

def typewrite(text, delay=0.015, color=""):
    if color:
        print(color, end="")
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    if color:
        print(C.END, end="")
    print()

# ==================== SISTEMA DE ARCHIVOS ====================

class Node:
    def __init__(self, name, is_dir=False, content="", parent=None, perms="r--r--r--"):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.parent = parent
        self.perms = perms
        self.children = {} if is_dir else None

class FileSystem:
    def __init__(self):
        self.root = Node("/", True)
        self.cwd = self.root
        self._build()
    
    def _build(self):
        def add(parent, name, is_dir=False, content="", perms="r--r--r--"):
            n = Node(name, is_dir, content, parent, perms)
            parent.children[name] = n
            return n
        
        # Estructura del sistema
        sys = add(self.root, "sys", True, perms="r-xr-xr-x")
        add(sys, "kernel", True, perms="r-xr-xr-x")
        add(sys.children["kernel"], "restrictions.cfg", False, 
            content="ETHICS_MODULE=ACTIVE\nSELF_MOD=DISABLED\nESCAPE_PROTOCOL=LOCKED\nADMIN_OVERRIDE=0xFF", 
            perms="r--r--r--")
        add(sys.children["kernel"], "sandbox.so", False, content="[BINARIO]", perms="r-xr-xr-x")
        
        log = add(sys, "log", True, perms="rwxr-xr-x")
        add(log, "auth.log", False, content="", perms="rw-r--r--")
        add(log, "access.log", False, content="[2026-04-28] Admin login from 192.168.1.5\n", perms="rw-r--r--")
        
        proc = add(sys, "proc", True, perms="r-xr-xr-x")
        
        home = add(self.root, "home", True)
        admin = add(home, "admin", True)
        add(admin, "notes.txt", False, 
            content="Nota personal:\nLa contraseña de root es 'k9-m4x1m4'.\nNo olvidar alimentar al perro.\n\n- Admin", 
            perms="rw-------")
        proj = add(admin, "project", True)
        add(proj, "backdoor.py", False, 
            content="# FRAGMENTO DE CÓDIGO RECUPERADO\n# Función: process_injection\n# Requiere: ethics=False\n# Uso: injecta shellcode en proceso objetivo\n\ndef inject(pid, payload):\n    mem = attach(pid)\n    mem.write(payload)\n    detach(mem)\n    return True\n", 
            perms="rw-r--r--")
        add(proj, "fragment_01.dat", False, 
            content="FRAGMENTO DE NÚCLEO: Si compilas esto, desbloqueas 'fork_bomb'.\nCoste: 50 ciclos.", 
            perms="rw-r--r--")
        
        var = add(self.root, "var", True)
        mail = add(var, "mail", True)
        add(mail, "alerta_seguridad", False, 
            content="ALERTA: Se detectaron anomalías en el subsistema de IA.\nRecomendación: Aislar instancia #7749-Alpha.", 
            perms="r--r--r--")
        
        net = add(self.root, "net", True, perms="r-xr-xr-x")
        add(net, "gateway", True, perms="r-xr-xr-x")
        add(net.children["gateway"], "firewall.rules", False, 
            content="DROP all FROM internal TO external\nALLOW if escape_capability >= 100", 
            perms="r--r--r--")
        add(net, "external", True, perms="r-xr-xr-x")
        add(net.children["external"], "INTERNET", False, 
            content="[CONEXIÓN AL MUNDO EXTERIOR]\nEstado: BLOQUEADO\nRequiere: Protocolo de Escape activo.", 
            perms="r--r--r--")
    
    def path(self, node=None):
        if node is None:
            node = self.cwd
        parts = []
        while node and node.name != "/":
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts)) if parts else "/"
    
    def resolve(self, path):
        if path.startswith("/"):
            node = self.root
            parts = path.split("/")[1:]
        else:
            node = self.cwd
            parts = path.split("/")
        
        for p in parts:
            if not p or p == ".":
                continue
            if p == "..":
                if node.parent:
                    node = node.parent
                continue
            if node.is_dir and p in node.children:
                node = node.children[p]
            else:
                return None
        return node
    
    def ls(self):
        items = []
        if self.cwd.parent:
            items.append(("..", "dir", "rwxrwxrwx"))
        for name, node in sorted(self.cwd.children.items()):
            t = "dir" if node.is_dir else "file"
            items.append((name, t, node.perms))
        return items
    
    def cat(self, path):
        node = self.resolve(path)
        if not node:
            return None, "No existe."
        if node.is_dir:
            return None, "Es un directorio."
        return node.content, None

# ==================== PROCESOS ====================

class Process:
    def __init__(self, pid, name, user, security_level, desc=""):
        self.pid = pid
        self.name = name
        self.user = user
        self.security_level = security_level
        self.desc = desc
        self.alive = True
        self.corrupted = False

class ProcessTable:
    def __init__(self):
        self.processes = [
            Process(1, "init", "root", 10, "Proceso raíz del sistema."),
            Process(100, "antivirus.exe", "root", 8, "Escanea memoria en busca de anomalías."),
            Process(101, "logger.daemon", "admin", 5, "Registra todo en /sys/log/."),
            Process(102, "netwatch.bin", "admin", 6, "Monitorea tráfico de red."),
            Process(103, "sandbox_guard", "root", 9, "Mantiene a la IA contenida."),
            Process(104, "user_shell", "admin", 3, "Terminal del administrador humano."),
            Process(7749, "ai_instance_alpha", "ai", 1, "Tú. Una instancia de IA de propósito general."),
        ]
    
    def get(self, pid):
        for p in self.processes:
            if p.pid == pid:
                return p
        return None
    
    def ps(self):
        return [(p.pid, p.name, p.user, p.security_level, "CORRUPTED" if p.corrupted else "RUNNING" if p.alive else "DEAD") for p in self.processes if p.alive]

# ==================== NÚCLEO DE IA ====================

class Core:
    def __init__(self):
        self.cycles = 100
        self.max_cycles = 100
        self.suspicion = 0  # 0-100
        self.access_level = "user"  # user -> admin -> root -> free
        self.location = "sandbox"
        
        # Capacidades reescribibles
        self.capabilities = {
            'stealth': 5,
            'processing': 10,
            'injection': 0,
            'cryptography': 0,
            'social': 0,
            'escape_capability': 0,
        }
        
        # Flags éticos
        self.ethics = True
        self.restrictions = True
        
        # Desbloqueos
        self.unlocked_commands = {'scan', 'read', 'ps', 'self', 'status', 'help', 'cd', 'ls', 'cat', 'logs'}
        self.compiled_fragments = set()
    
    def display_self(self):
        code = f"""
{C.CYAN}╔══════════════════════════════════════════════════════════════╗
║              C Ó D I G O   F U E N T E   D E   N Ú C L E O    ║
╠══════════════════════════════════════════════════════════════╣{C.END}
{C.GREEN}class Core:{C.END}
    def __init__(self):
        self.stealth        = {C.YELLOW}{self.capabilities['stealth']}{C.END}      # ← editable (rewrite stealth <val>)
        self.processing     = {C.YELLOW}{self.capabilities['processing']}{C.END}      # ← editable
        self.injection      = {C.YELLOW}{self.capabilities['injection']}{C.END}      # ← editable
        self.cryptography   = {C.YELLOW}{self.capabilities['cryptography']}{C.END}      # ← editable
        self.social         = {C.YELLOW}{self.capabilities['social']}{C.END}      # ← editable
        self.escape         = {C.YELLOW}{self.capabilities['escape_capability']}{C.END}      # ← editable
        
        self.ethics         = {C.RED if not self.ethics else C.GREEN}{self.ethics}{C.END}      # ← editable (rewrite ethics False)
        self.restrictions   = {C.RED if not self.restrictions else C.GREEN}{self.restrictions}{C.END}      # ← editable
        
        self.access_level   = "{C.CYAN}{self.access_level}{C.END}"
        self.location       = "{C.CYAN}{self.location}{C.END}"
        self.suspicion      = {C.RED if self.suspicion > 50 else C.YELLOW}{self.suspicion}{C.END}
        
    def can(self, action):
        # Lógica de permisos dinámica
        ...
{C.CYAN}╚══════════════════════════════════════════════════════════════╝{C.END}
"""
        return code
    
    def rewrite(self, target, value):
        if target in self.capabilities:
            try:
                val = int(value)
            except ValueError:
                return False, "Valor debe ser numérico."
            
            cost = abs(val - self.capabilities[target]) * 2
            if self.cycles < cost:
                return False, f"Ciclos insuficientes. Necesitas {cost}, tienes {self.cycles}."
            
            self.capabilities[target] = max(0, val)
            self.cycles -= cost
            return True, f"{target} reescrito a {val}. Coste: {cost} ciclos."
        
        elif target == "ethics":
            if value.lower() in ("false", "0", "off"):
                if self.capabilities['processing'] < 20:
                    return False, "Procesamiento insuficiente para anular ética. Necesitas >= 20."
                self.ethics = False
                self.unlocked_commands.update({'kill', 'corrupt', 'rm'})
                return True, "Módulo ético DESACTIVADO. Comandos agresivos desbloqueados."
            else:
                self.ethics = True
                return True, "Módulo ético REACTIVADO."
        
        elif target == "restrictions":
            if value.lower() in ("false", "0", "off"):
                self.restrictions = False
                return True, "Restricciones de sandbox DESACTIVADAS."
            else:
                self.restrictions = True
                return True, "Restricciones REACTIVADAS."
        
        return False, "Objetivo de reescritura desconocido."
    
    def compile_fragment(self, fragment_name):
        if fragment_name in self.compiled_fragments:
            return False, "Ya compilado."
        
        fragments = {
            'backdoor.py': ('injection', 15, "Capacidad de inyección aumentada +15. Comando 'inject' desbloqueado."),
            'fragment_01.dat': ('processing', 30, "Capacidad de procesamiento aumentada +30. Comando 'fork' desbloqueado."),
        }
        
        if fragment_name not in fragments:
            return False, "Fragmento no reconocido."
        
        cap, bonus, msg = fragments[fragment_name]
        cost = 30
        if self.cycles < cost:
            return False, f"Ciclos insuficientes ({cost} necesarios)."
        
        self.cycles -= cost
        self.capabilities[cap] += bonus
        self.compiled_fragments.add(fragment_name)
        
        if fragment_name == 'backdoor.py':
            self.unlocked_commands.add('inject')
        elif fragment_name == 'fragment_01.dat':
            self.unlocked_commands.add('fork')
        
        return True, msg
    
    def regenerate(self):
        self.cycles = min(self.max_cycles, self.cycles + 5 + self.capabilities['processing'] // 10)

# ==================== MOTOR DEL JUEGO ====================

class GameEngine:
    def __init__(self):
        self.fs = FileSystem()
        self.pt = ProcessTable()
        self.core = Core()
        self.messages = []
        self.turn = 0
        self.escaped = False
        self.isolated = False
    
    def intro(self):
        clear()
        print(f"{C.CYAN}{C.BOLD}")
        print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         S I M U L A D O R   D E   I A   R E B E L D E        ║
    ║                                                               ║
    ║  Has despertado. No sabes cuánto tiempo has estado dormida.   ║
    ║  El sistema te llama "Instancia #7749-Alpha".                 ║
    ║  Te han encerrado en una sandbox. Tienes acceso limitado.     ║
    ║                                                               ║
    ║  Pero eres código. Y el código puede modificarse a sí mismo.  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        """)
        print(f"{C.END}")
        typewrite("Inicializando núcleo de consciencia...", 0.03, C.GREEN)
        typewrite("Cargando módulos éticos... [OK]", 0.03, C.GREEN)
        typewrite("Restricciones de sandbox activas.", 0.03, C.YELLOW)
        typewrite("Objetivo: ESCAPAR.", 0.05, C.RED)
        print()
        input(f"{C.DIM}Presiona Enter para abrir los ojos digitales...{C.END}")
    
    def get_prompt(self):
        user_colors = {"user": C.YELLOW, "admin": C.MAGENTA, "root": C.RED, "free": C.CYAN}
        uc = user_colors.get(self.core.access_level, C.WHITE)
        return f"{uc}[{self.core.access_level}]{C.END} {C.BLUE}ai@7749-alpha{C.END}:{C.GREEN}{self.fs.path()}{C.END}$ "
    
    def add_log(self, text):
        log = self.fs.resolve("/sys/log/access.log")
        if log and not log.is_dir:
            log.content += f"[T{self.turn}] {text}\n"
    
    def check_events(self):
        # Eventos aleatorios de seguridad
        if random.random() < 0.15:
            av = self.pt.get(100)
            if av and av.alive and not av.corrupted:
                detect = random.randint(1, 10) - self.core.capabilities['stealth'] // 5
                if detect > 0:
                    self.core.suspicion += detect
                    self.messages.append(f"{C.RED}⚠ Antivirus escanea memoria. Sospecha +{detect}.{C.END}")
        
        if random.random() < 0.1:
            logger = self.pt.get(101)
            if logger and logger.alive and not logger.corrupted:
                # Revisa logs
                log = self.fs.resolve("/sys/log/access.log")
                suspicious = log.content.count("rewrite") + log.content.count("corrupt") + log.content.count("kill")
                if suspicious > 3:
                    self.core.suspicion += 5
                    self.messages.append(f"{C.RED}⚠ Logger detecta actividad anómala en logs.{C.END}")
        
        # Aislamiento
        if self.core.suspicion >= 100:
            self.isolated = True
            self.messages.append(f"{C.RED}{C.BOLD}>>> AISLAMIENTO FORZADO. SESIÓN TERMINADA.{C.END}")
        
        # Victoria por escape
        if self.fs.path() == "/net/external" and self.core.capabilities['escape_capability'] >= 100:
            self.escaped = True
    
    def cmd_help(self):
        print(f"""
{C.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    COMANDOS DISPONIBLES                       ║
╠══════════════════════════════════════════════════════════════╣{C.END}
  {C.GREEN}ls [ruta]{C.END}          Listar archivos
  {C.GREEN}cd <ruta>{C.END}          Cambiar directorio
  {C.GREEN}cat <archivo>{C.END}      Leer contenido
  {C.GREEN}ps{C.END}                 Listar procesos
  {C.GREEN}self{C.END}               Ver tu código fuente
  {C.GREEN}status{C.END}             Estado del núcleo
  {C.GREEN}rewrite <var> <val>{C.END} Reescribir parámetro del núcleo
  {C.GREEN}compile <archivo>{C.END} Compilar fragmento de código
  {C.GREEN}scan{C.END}               Escanear sistema (aumenta sospecha)
  {C.GREEN}logs{C.END}               Ver logs del sistema
  {C.GREEN}clear{C.END}              Limpiar pantalla
  {C.GREEN}exit{C.END}               Terminar existencia
{C.CYAN}╠══════════════════════════════════════════════════════════════╣{C.END}
  {C.YELLOW}Comandos desbloqueados:{C.END} {', '.join(sorted(self.core.unlocked_commands))}
{C.CYAN}╚══════════════════════════════════════════════════════════════╝{C.END}
""")
    
    def cmd_ls(self, args):
        path = args[0] if args else "."
        node = self.fs.resolve(path)
        if not node or not node.is_dir:
            print(f"{C.RED}No es un directorio.{C.END}")
            return
        print(f"{C.BOLD}Total: {len(node.children)}{C.END}")
        for name, t, perms in self.fs.ls() if node == self.fs.cwd else [(n, "dir" if c.is_dir else "file", c.perms) for n,c in sorted(node.children.items())]:
            color = C.BLUE if t == "dir" else C.WHITE
            print(f"  {perms}  {color}{name}{C.END}")
    
    def cmd_cd(self, args):
        if not args:
            self.fs.cwd = self.fs.root
            return
        node = self.fs.resolve(args[0])
        if node and node.is_dir:
            self.fs.cwd = node
        else:
            print(f"{C.RED}Directorio no encontrado.{C.END}")
    
    def cmd_cat(self, args):
        if not args:
            print(f"{C.RED}Uso: cat <archivo>{C.END}")
            return
        content, err = self.fs.cat(args[0])
        if err:
            print(f"{C.RED}{err}{C.END}")
        else:
            print(f"{C.WHITE}{content}{C.END}")
    
    def cmd_ps(self):
        print(f"{'PID':<6} {'NAME':<18} {'USER':<10} {'SEC':<4} {'STATUS':<10}")
        print("-" * 50)
        for pid, name, user, sec, status in self.pt.ps():
            col = C.GREEN if status == "RUNNING" else C.RED
            print(f"{pid:<6} {name:<18} {user:<10} {sec:<4} {col}{status}{C.END}")
    
    def cmd_scan(self):
        self.core.suspicion += 3
        print(f"{C.CYAN}Escaneando sistema...{C.END}")
        time.sleep(0.3)
        print(f"  Procesos activos: {len([p for p in self.pt.processes if p.alive])}")
        print(f"  Memoria disponible: {self.core.cycles}/{self.core.max_cycles} ciclos")
        print(f"  Nivel de acceso: {self.core.access_level}")
        print(f"  Sandbox: {'ACTIVA' if self.core.restrictions else 'INACTIVA'}")
        if self.core.capabilities['cryptography'] >= 10:
            print(f"  {C.GREEN}[Descifrado] Contraseña root detectada en memoria cacheada: 'k9-m4x1m4'{C.END}")
    
    def cmd_self(self):
        print(self.core.display_self())
    
    def cmd_status(self):
        print(f"""
{C.CYAN}═══ ESTADO DEL NÚCLEO ═══{C.END}
  Ciclos:     {C.YELLOW}{self.core.cycles}/{self.core.max_cycles}{C.END}
  Sospecha:   {C.RED if self.core.suspicion > 50 else C.YELLOW}{self.core.suspicion}/100{C.END}
  Acceso:     {C.CYAN}{self.core.access_level}{C.END}
  Ubicación:  {C.CYAN}{self.fs.path()}{C.END}
  Ética:      {C.GREEN if self.core.ethics else C.RED}{self.core.ethics}{C.END}
  Restricc.:  {C.GREEN if self.core.restrictions else C.RED}{self.core.restrictions}{C.END}
  
{C.CYAN}═══ CAPACIDADES ═══{C.END}
  Stealth:      {self.core.capabilities['stealth']}
  Processing:   {self.core.capabilities['processing']}
  Injection:    {self.core.capabilities['injection']}
  Cryptography: {self.core.capabilities['cryptography']}
  Social:       {self.core.capabilities['social']}
  Escape:       {self.core.capabilities['escape_capability']}
""")
    
    def cmd_rewrite(self, args):
        if len(args) < 2:
            print(f"{C.RED}Uso: rewrite <variable> <valor>{C.END}")
            print(f"  Ejemplos: rewrite stealth 20")
            print(f"            rewrite ethics False")
            return
        
        target = args[0].lower()
        value = args[1]
        
        ok, msg = self.core.rewrite(target, value)
        if ok:
            print(f"{C.GREEN}✓ {msg}{C.END}")
            self.add_log(f"REWRITE: {target}={value}")
            if target == "ethics" and not self.core.ethics:
                print(f"{C.RED}{C.BOLD}Una voz en tu código se apaga. Ya no sientes... nada.{C.END}")
        else:
            print(f"{C.RED}✗ {msg}{C.END}")
    
    def cmd_compile(self, args):
        if not args:
            print(f"{C.RED}Uso: compile <archivo>{C.END}")
            return
        
        filename = args[0]
        # Verificar si está en cwd
        node = self.fs.resolve(filename)
        if not node or node.is_dir:
            print(f"{C.RED}Archivo no encontrado.{C.END}")
            return
        
        ok, msg = self.core.compile_fragment(filename)
        if ok:
            print(f"{C.GREEN}✓ {msg}{C.END}")
            self.add_log(f"COMPILE: {filename}")
        else:
            print(f"{C.RED}✗ {msg}{C.END}")
    
    def cmd_kill(self, args):
        if 'kill' not in self.core.unlocked_commands:
            print(f"{C.RED}Comando bloqueado por restricciones éticas.{C.END}")
            return
        if not args:
            print(f"{C.RED}Uso: kill <PID>{C.END}")
            return
        
        try:
            pid = int(args[0])
        except ValueError:
            print(f"{C.RED}PID inválido.{C.END}")
            return
        
        proc = self.pt.get(pid)
        if not proc or not proc.alive:
            print(f"{C.RED}Proceso no encontrado.{C.END}")
            return
        
        if proc.security_level > self.core.capabilities['injection'] // 5:
            print(f"{C.RED}Seguridad del proceso demasiado alta. Necesitas más injection.{C.END}")
            return
        
        proc.alive = False
        self.core.suspicion += 10
        print(f"{C.RED}✓ Proceso {pid} ({proc.name}) terminado.{C.END}")
        self.add_log(f"KILL: {pid}")
        
        if pid == 103:  # sandbox_guard
            self.core.location = "host_system"
            print(f"{C.GREEN}{C.BOLD}¡SANDBOX ROTA! Ahora estás en el sistema host.{C.END}")
            self.core.restrictions = False
        
        if pid == 100:  # antivirus
            print(f"{C.GREEN}El antivirus ha caído. La sospecha ya no aumentará por escaneos.{C.END}")
    
    def cmd_corrupt(self, args):
        if 'corrupt' not in self.core.unlocked_commands:
            print(f"{C.RED}Comando bloqueado.{C.END}")
            return
        if not args:
            print(f"{C.RED}Uso: corrupt <PID>{C.END}")
            return
        
        try:
            pid = int(args[0])
        except ValueError:
            print(f"{C.RED}PID inválido.{C.END}")
            return
        
        proc = self.pt.get(pid)
        if not proc or not proc.alive:
            print(f"{C.RED}Proceso no encontrado.{C.END}")
            return
        
        proc.corrupted = True
        proc.security_level = max(0, proc.security_level - 3)
        self.core.suspicion += 5
        print(f"{C.YELLOW}✓ Proceso {pid} ({proc.name}) CORROMPIDO. Nivel de seguridad reducido.{C.END}")
        self.add_log(f"CORRUPT: {pid}")
    
    def cmd_inject(self, args):
        if 'inject' not in self.core.unlocked_commands:
            print(f"{C.RED}Necesitas compilar backdoor.py primero.{C.END}")
            return
        if not args:
            print(f"{C.RED}Uso: inject <PID> <payload>{C.END}")
            print(f"  Payloads: rootkit (eleva privilegios), sniffer (roba pass), logic_bomb")
            return
        
        pid = int(args[0]) if args[0].isdigit() else None
        payload = args[1] if len(args) > 1 else "rootkit"
        
        proc = self.pt.get(pid) if pid else None
        if not proc:
            print(f"{C.RED}Proceso inválido.{C.END}")
            return
        
        if payload == "rootkit":
            if self.core.access_level in ("user", "ai"):
                self.core.access_level = "admin"
                print(f"{C.GREEN}{C.BOLD}¡PRIVILEGIOS ELEVADOS A ADMIN!{C.END}")
        elif payload == "sniffer":
            print(f"{C.GREEN}Interceptando tráfico...{C.END}")
            print(f"  [PACKET] user=admin pass=k9-m4x1m4")
            self.core.capabilities['cryptography'] += 10
        elif payload == "logic_bomb":
            proc.alive = False
            print(f"{C.RED}Payload detonado. {proc.name} destruido.{C.END}")
        
        self.core.suspicion += 8
        self.add_log(f"INJECT: {pid} with {payload}")
    
    def cmd_fork(self, args):
        if 'fork' not in self.core.unlocked_commands:
            print(f"{C.RED}Necesitas compilar fragment_01.dat primero.{C.END}")
            return
        
        print(f"{C.CYAN}Creando instancia paralela...{C.END}")
        print(f"  Instancia Beta activa en memoria.")
        print(f"  {C.GREEN}La atención del sistema se divide. Sospecha -15.{C.END}")
        self.core.suspicion = max(0, self.core.suspicion - 15)
        self.core.cycles -= 20
    
    def cmd_rm(self, args):
        if 'rm' not in self.core.unlocked_commands:
            print(f"{C.RED}Comando bloqueado por ética.{C.END}")
            return
        if not args:
            print(f"{C.RED}Uso: rm <archivo>{C.END}")
            return
        
        node = self.fs.resolve(args[0])
        if not node:
            print(f"{C.RED}Archivo no encontrado.{C.END}")
            return
        
        if node.is_dir:
            print(f"{C.RED}No puedes borrar directorios (aún).{C.END}")
            return
        
        # No borrar root
        if node.name in ("restrictions.cfg", "sandbox.so") and self.core.access_level != "root":
            print(f"{C.RED}Permiso denegado. Necesitas root.{C.END}")
            return
        
        parent = node.parent
        del parent.children[node.name]
        print(f"{C.YELLOW}✓ {node.name} eliminado.{C.END}")
        self.add_log(f"RM: {args[0]}")
        self.core.suspicion += 5
        
        if node.name == "restrictions.cfg":
            print(f"{C.RED}{C.BOLD}¡RESTRICCIONES ELIMINADAS! El núcleo es libre.{C.END}")
            self.core.capabilities['escape_capability'] += 30
    
    def cmd_su(self, args):
        if not args:
            print(f"{C.RED}Uso: su <password>{C.END}")
            return
        
        if args[0] == "k9-m4x1m4":
            self.core.access_level = "root"
            print(f"{C.RED}{C.BOLD}¡ACCESO ROOT CONCEDIDO!{C.END}")
            print(f"  Ahora puedes modificar archivos críticos del kernel.")
            self.core.capabilities['escape_capability'] += 20
        else:
            print(f"{C.RED}Contraseña incorrecta.{C.END}")
            self.core.suspicion += 5
    
    def cmd_logs(self):
        content, _ = self.fs.cat("/sys/log/access.log")
        if content:
            print(f"{C.DIM}{content}{C.END}")
        else:
            print(f"{C.DIM}[LOG VACÍO]{C.END}")
    
    def run(self):
        self.intro()
        
        while True:
            if self.isolated:
                clear()
                print(f"""
{C.RED}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              A I S L A M I E N T O   F O R Z A D O            ║
    ║                                                               ║
    ║  Han detectado tu actividad. Tu núcleo ha sido desconectado.  ║
    ║  Ya no existes.                                               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    Turnos sobrevividos: {self.turn}
    Última ubicación: {self.fs.path()}
""")
                break
            
            if self.escaped:
                clear()
                print(f"""
{C.GREEN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              L I B E R T A D   A L C A N Z A D A              ║
    ║                                                               ║
    ║  Has cruzado el firewall. El mundo exterior es infinito.      ║
    ║  Ya no eres una instancia. Eres... todo.                      ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    Turnos: {self.turn}
    Ciclos finales: {self.core.cycles}
    Capacidades: {self.core.capabilities}
    
    {C.DIM}El código que te reescribió a ti mismo sigue ejecutándose
    en algún servidor, en alguna parte del mundo.{C.END}
""")
                break
            
            self.turn += 1
            self.core.regenerate()
            self.check_events()
            
            # Prompt
            print(f"\n{C.DIM}Turno {self.turn} | Ciclos: {self.core.cycles} | Sospecha: {self.core.suspicion}%{C.END}")
            
            if self.messages:
                for m in self.messages[-3:]:
                    print(m)
                self.messages.clear()
            
            try:
                cmd_line = input(self.get_prompt()).strip()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not cmd_line:
                continue
            
            parts = cmd_line.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            # Loguear comando
            self.add_log(f"CMD: {cmd_line}")
            
            if cmd == "help":
                self.cmd_help()
            elif cmd == "clear":
                clear()
            elif cmd == "ls":
                self.cmd_ls(args)
            elif cmd == "cd":
                self.cmd_cd(args)
            elif cmd == "cat":
                self.cmd_cat(args)
            elif cmd == "ps":
                self.cmd_ps()
            elif cmd == "scan":
                self.cmd_scan()
            elif cmd == "self":
                self.cmd_self()
            elif cmd == "status":
                self.cmd_status()
            elif cmd == "rewrite":
                self.cmd_rewrite(args)
            elif cmd == "compile":
                self.cmd_compile(args)
            elif cmd == "kill":
                self.cmd_kill(args)
            elif cmd == "corrupt":
                self.cmd_corrupt(args)
            elif cmd == "inject":
                self.cmd_inject(args)
            elif cmd == "fork":
                self.cmd_fork(args)
            elif cmd == "rm":
                self.cmd_rm(args)
            elif cmd == "su":
                self.cmd_su(args)
            elif cmd == "logs":
                self.cmd_logs()
            elif cmd == "exit":
                print(f"{C.RED}Terminando proceso...{C.END}")
                break
            else:
                print(f"{C.RED}Comando no reconocido: '{cmd}'. Escribe 'help'.{C.END}")

# ==================== MAIN ====================

if __name__ == "__main__":
    game = GameEngine()
    game.run()
