#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUGGER: EL JUEGO
Eres un debugger dentro de un sistema operativo corrupto.
Inspecciona funciones, repara bugs, evita el kernel panic.
"""

import os
import sys
import time

class C:
    END = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"
    WHITE = "\033[97m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class BugType:
    NONE = 0; BAD_VALUE = 1; INFINITE_LOOP = 2
    DIV_ZERO = 3; OFF_BY_ONE = 4; BUFFER_OVERFLOW = 5

class Function:
    def __init__(self, name, lines, variables, bug_type, bug_line, fix_hint):
        self.name = name
        self.lines = lines
        self.variables = dict(variables)
        self.bug_type = bug_type
        self.bug_line = bug_line  # 0-based
        self.fix_hint = fix_hint
        self.fixed = False
        self.pc = 0
        self.trapped = False

    def is_call(self, line):
        s = line.strip()
        if s.endswith('();') and not s.startswith('//'):
            return s.split('(')[0].strip()
        return None

class DebuggerGame:
    def __init__(self):
        self.cycles = 500
        self.fixed_count = 0
        self.current = 'main'
        self.unlocked = {'main'}
        self.functions = self._build_functions()
        self.game_over_flag = False

    def _build_functions(self):
        funcs = {}

        funcs['main'] = Function(
            'main',
            [
                "void main() {",
                "    int error_count = 0;",
                "    boot_sequence();",
                "    error_count = 999; // [ANOMALY]",
                "    if (error_count == 0) {",
                "        proceed_normal();",
                "    } else {",
                "        kernel_panic();",
                "    }",
                "    return;",
                "}"
            ],
            {'error_count': 0},
            BugType.BAD_VALUE,
            3,
            "Restored error_count initialization to 0."
        )

        funcs['auth_loop'] = Function(
            'auth_loop',
            [
                "void auth_loop() {",
                "    int attempts = 0;",
                "    while (1) { // [SUSPICIOUS]",
                "        validate_token();",
                "        // FIXME: missing break condition",
                "    }",
                "    return;",
                "}"
            ],
            {'attempts': 0},
            BugType.INFINITE_LOOP,
            2,
            "Injected exit condition: while (attempts < 3)."
        )

        funcs['calc_average'] = Function(
            'calc_average',
            [
                "int calc_average() {",
                "    int total = 100;",
                "    int count = 0; // [SUSPICIOUS]",
                "    int avg = total / count;",
                "    return avg;",
                "}"
            ],
            {'total': 100, 'count': 0, 'avg': 0},
            BugType.DIV_ZERO,
            3,
            "Added guard: if (count == 0) return 0;"
        )

        funcs['render_frame'] = Function(
            'render_frame',
            [
                "void render_frame() {",
                "    int i;",
                "    for (i = 0; i <= 10; i++) { // [SUSPICIOUS]",
                "        vram_write(i);",
                "    }",
                "}"
            ],
            {'i': 0, 'MAX': 10},
            BugType.OFF_BY_ONE,
            2,
            "Fixed boundary: i < 10 instead of i <= 10."
        )

        funcs['kernel_main'] = Function(
            'kernel_main',
            [
                "void kernel_main() {",
                "    char buffer[8];",
                "    char *input = \"OVERRIDE_SEQUENCE_TOO_LONG\";",
                "    strcpy(buffer, input); // [CRITICAL]",
                "    execute(buffer);",
                "}"
            ],
            {'buffer_size': 8},
            BugType.BUFFER_OVERFLOW,
            3,
            "Replaced strcpy with strncpy(buffer, input, 7)."
        )

        return funcs

    def cur(self):
        return self.functions[self.current]

    def prompt(self):
        ccolor = C.GREEN if self.cycles > 200 else C.YELLOW if self.cycles > 100 else C.RED
        return f"{C.DIM}(dbg){C.END} {C.CYAN}{self.current}{C.END} {ccolor}[{self.cycles}]{C.END}> "

    def header(self):
        clear()
        print(f"{C.BLUE}{C.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              D E B U G G E R :   E L   J U E G O             ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"{C.END}")
        print(f"  Ciclos CPU: {C.YELLOW}{self.cycles}{C.END}  |  "
              f"Funciones reparadas: {C.GREEN}{self.fixed_count}/5{C.END}  |  "
              f"Ubicación: {C.CYAN}{self.current}{C.END}")
        print(f"  Desbloqueadas: {', '.join(sorted(self.unlocked))}")
        print()

    def list_code(self):
        f = self.cur()
        print(f"{C.BOLD}{C.WHITE}Código fuente de '{f.name}':{C.END}")
        status = f"{C.GREEN}[PATCHED]{C.END}" if f.fixed else f"{C.RED}[BUGGY]{C.END}"
        print(f"  Estado: {status}")
        print()
        for i, line in enumerate(f.lines, 1):
            marker = "   "
            if i-1 == f.pc:
                marker = f"{C.YELLOW} > {C.END}"
            num = f"{C.DIM}{i:2}{C.END}"
            print(f"{marker}{num}  {line}")
        print()

    def inspect_var(self, name):
        f = self.cur()
        if name in f.variables:
            print(f"  {C.CYAN}{name}{C.END} = {C.YELLOW}{f.variables[name]}{C.END}")
        else:
            print(f"  {C.RED}Variable '{name}' no encontrada en ámbito.{C.END}")

    def set_var(self, name, val):
        f = self.cur()
        if name not in f.variables:
            print(f"  {C.RED}Variable '{name}' no existe aquí.{C.END}")
            return
        try:
            # Intentar int
            f.variables[name] = int(val)
        except ValueError:
            f.variables[name] = val
        print(f"  {C.GREEN}{name} = {f.variables[name]}{C.END}")

    def trigger_bug(self, func):
        if func.bug_type == BugType.BAD_VALUE:
            print(f"  {C.YELLOW}[ANOMALY] error_count corrompido a 999{C.END}")
            func.variables['error_count'] = 999
        elif func.bug_type == BugType.INFINITE_LOOP:
            func.trapped = True
            print(f"  {C.RED}[TRAP] ¡Loop infinito detectado!{C.END}")
            print(f"  El contador de programa está atascado en línea {func.bug_line+1}.")
            print(f"  Usa 'fix' para inyectar condición de salida.")
        elif func.bug_type == BugType.DIV_ZERO:
            print(f"  {C.RED}[EXCEPTION] División por cero en línea {func.bug_line+1}{C.END}")
            self.cycles -= 50
            func.variables['avg'] = 0
        elif func.bug_type == BugType.OFF_BY_ONE:
            print(f"  {C.RED}[WARNING] Off-by-one: escritura fuera de VRAM{C.END}")
            self.cycles -= 25
        elif func.bug_type == BugType.BUFFER_OVERFLOW:
            print(f"  {C.RED}[SEGFAULT] Buffer overflow en línea {func.bug_line+1}{C.END}")
            print(f"  {C.RED}Sistema inestable.{C.END}")
            self.cycles -= 100

    def cmd_step(self):
        f = self.cur()
        if f.trapped:
            self.cycles -= 15
            print(f"  {C.RED}Atrapado en loop infinito. CPU drenándose... (-15 ciclos){C.END}")
            return

        if f.pc >= len(f.lines):
            print(f"  {C.DIM}Fin de función. Usa 'goto' o 'back'.{C.END}")
            return

        line = f.lines[f.pc]

        # ¿Línea buggy?
        if f.pc == f.bug_line and not f.fixed:
            self.trigger_bug(f)
            if not f.trapped:
                f.pc += 1
        else:
            call = f.is_call(line)
            if call and call in self.functions:
                print(f"  {C.CYAN}[Call] {call}() detectado. Usa 'goto {call}' para entrar.{C.END}")
            f.pc += 1

        self.cycles -= 1

    def cmd_run(self):
        f = self.cur()
        if f.trapped:
            print(f"  {C.RED}No se puede ejecutar: función atrapada en loop infinito.{C.END}")
            return

        max_steps = 50
        for _ in range(max_steps):
            if f.pc >= len(f.lines):
                print(f"  {C.GREEN}[Function returned]{C.END}")
                return

            # ¿Bug por delante?
            if f.pc == f.bug_line and not f.fixed:
                print(f"  {C.YELLOW}Ejecución detenida antes de código sospechoso:{C.END}")
                print(f"    Línea {f.bug_line+1}: {f.lines[f.bug_line]}")
                print(f"  {C.DIM}Usa 'step' para ejecutar (riesgoso) o 'fix' para parchear.{C.END}")
                return

            # Llamada a función
            call = f.is_call(f.lines[f.pc])
            if call and call in self.functions:
                print(f"  {C.CYAN}Ejecución detenida en llamada a {call}(){C.END}")
                return

            f.pc += 1
            self.cycles -= 1
            if self.cycles <= 0:
                return

        print(f"  {C.RED}Run timeout: posible loop infinito o ruta muy larga.{C.END}")

    def cmd_fix(self):
        f = self.cur()
        if f.fixed:
            print(f"  {C.YELLOW}Función ya parcheada.{C.END}")
            return

        f.fixed = True
        f.trapped = False
        self.fixed_count += 1
        self.cycles += 50
        print(f"  {C.GREEN}{C.BOLD}[PATCH APLICADO]{C.END} {f.name} reparada.")
        print(f"  {C.DIM}{f.fix_hint}{C.END}")

        # Desbloquear siguiente
        order = ['main', 'auth_loop', 'calc_average', 'render_frame', 'kernel_main']
        if f.name in order:
            idx = order.index(f.name)
            if idx + 1 < len(order):
                nxt = order[idx+1]
                if nxt not in self.unlocked:
                    self.unlocked.add(nxt)
                    print(f"  {C.CYAN}[UNLOCKED] Función '{nxt}' accesible.{C.END}")

        if self.fixed_count >= 5:
            self.win()

    def cmd_goto(self, target):
        if target not in self.functions:
            print(f"  {C.RED}Función '{target}' no existe.{C.END}")
            return
        if target not in self.unlocked:
            print(f"  {C.RED}Función '{target}' bloqueada. Repara funciones previas.{C.END}")
            return
        self.current = target
        print(f"  {C.CYAN}Situado en {target}(){C.END}")

    def cmd_back(self):
        order = ['main', 'auth_loop', 'calc_average', 'render_frame', 'kernel_main']
        if self.current in order:
            idx = order.index(self.current)
            if idx > 0:
                self.cmd_goto(order[idx-1])
                return
        self.cmd_goto('main')

    def win(self):
        clear()
        print(f"""
{C.GREEN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           S I S T E M A   R E S T A U R A D O                 ║
    ║                                                               ║
    ║  Has parcheado el núcleo. El kernel vuelve a respirar.        ║
    ║  El debugger puede dormir. El sistema vive.                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    Ciclos restantes: {self.cycles}
    Bugs corregidos: {self.fixed_count}
    Eres el mejor debugger que ha contratado esta empresa.
        """)
        sys.exit(0)

    def lose(self):
        clear()
        print(f"""
{C.RED}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              K E R N E L   P A N I C                          ║
    ║                                                               ║
    ║  Los ciclos de CPU se han agotado.                            ║
    ║  El sistema ha colapsado.                                     ║
    ║  Tu existencia como debugger ha sido... desinstalada.         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.END}
    Bugs reparados: {self.fixed_count}/5
    Última función: {self.current}
        """)
        sys.exit(0)

    def help(self):
        print(f"""
{C.CYAN}{C.BOLD}═══════════════════════════════════════════════════════════════{C.END}
  Comandos de depuración:

  {C.GREEN}list, l{C.END}              Mostrar código de la función actual
  {C.GREEN}inspect <var>, i <var>{C.END}  Inspeccionar variable
  {C.GREEN}set <var> <val>{C.END}      Modificar variable (¡cuidado!)
  {C.GREEN}step, s{C.END}              Ejecutar siguiente línea
  {C.GREEN}run, r{C.END}               Ejecutar hasta bug o retorno
  {C.GREEN}fix, f{C.END}               Aplicar parche a función actual
  {C.GREEN}goto <func>, g <func>{C.END} Moverse a otra función
  {C.GREEN}back, b{C.END}              Volver a función anterior
  {C.GREEN}status{C.END}               Estado del sistema
  {C.GREEN}help, h{C.END}              Esta ayuda
  {C.GREEN}quit, q{C.END}              Abortar sesión
{C.CYAN}{C.BOLD}═══════════════════════════════════════════════════════════════{C.END}
  Consejo: Usa 'list' para leer el código. 'inspect' para ver datos.
  'run' se detiene antes de ejecutar código buggy. 'step' lo ejecuta.
""")

    def run(self):
        clear()
        print(f"""{C.BLUE}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        D E B U G G E R :   E L   J U E G O                    ║
    ║                                                               ║
    ║  Bienvenido, agente de depuración.                            ║
    ║  El sistema operativo ha sufrido múltiples corrupciones.      ║
    ║  Tu misión: navegar las funciones, inspeccionar variables,    ║
    ║  y aplicar parches antes de que los ciclos de CPU se agoten.  ║
    ║                                                               ║
    ║  Escribe 'help' para ver los comandos disponibles.            ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        {C.END}""")
        input(f"{C.DIM}Presiona Enter para cargar el entorno de depuración...{C.END}")

        while not self.game_over_flag:
            if self.cycles <= 0:
                self.lose()
                return

            self.header()
            self.list_code()

            try:
                cmd_line = input(self.prompt()).strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not cmd_line:
                continue

            parts = cmd_line.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ('help', 'h'):
                self.help()
            elif cmd in ('list', 'l'):
                pass  # ya se muestra en header
            elif cmd in ('inspect', 'i'):
                if args:
                    self.inspect_var(args[0])
                else:
                    print(f"  {C.RED}Uso: inspect <variable>{C.END}")
            elif cmd == 'set':
                if len(args) >= 2:
                    self.set_var(args[0], ' '.join(args[1:]))
                else:
                    print(f"  {C.RED}Uso: set <var> <valor>{C.END}")
            elif cmd in ('step', 's'):
                self.cmd_step()
            elif cmd in ('run', 'r'):
                self.cmd_run()
            elif cmd in ('fix', 'f'):
                self.cmd_fix()
            elif cmd in ('goto', 'g'):
                if args:
                    self.cmd_goto(args[0])
                else:
                    print(f"  {C.RED}Uso: goto <función>{C.END}")
            elif cmd in ('back', 'b'):
                self.cmd_back()
            elif cmd == 'status':
                print(f"  Ciclos: {self.cycles}")
                print(f"  Función: {self.current}")
                print(f"  PC: {self.cur().pc + 1}")
                print(f"  Reparadas: {self.fixed_count}/5")
            elif cmd in ('quit', 'q', 'exit'):
                print(f"{C.RED}Sesión terminada.{C.END}")
                break
            else:
                print(f"  {C.RED}Comando desconocido: '{cmd}'{C.END}")

            input(f"\n{C.DIM}Presiona Enter para continuar...{C.END}")

if __name__ == "__main__":
    game = DebuggerGame()
    game.run()
