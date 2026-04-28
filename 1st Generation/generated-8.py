#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMULADOR DE MERCADO CAÓTICO
Exchange de commodities absurdas. Clima, memes y bots automáticos.
"""

import os
import sys
import time
import random

# ==================== VISUALES ====================

class C:
    END = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"
    WHITE = "\033[97m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== ACTIVOS ====================

class Asset:
    def __init__(self, symbol, name, base_price, volatility):
        self.symbol = symbol
        self.name = name
        self.price = float(base_price)
        self.prev_price = float(base_price)
        self.volatility = volatility
        self.history = [base_price]
    
    def fluctuate(self, event_mod=0.0, climate_mod=0.0):
        self.prev_price = self.price
        # Ruido gaussiano + momentum
        noise = random.gauss(0, self.volatility)
        momentum = 0.0
        if len(self.history) >= 2:
            mom = (self.history[-1] - self.history[-2]) / self.history[-2]
            momentum = mom * 0.25
        change = noise + momentum + event_mod + climate_mod
        self.price = max(0.01, self.price * (1.0 + change))
        self.history.append(self.price)
        if len(self.history) > 15:
            self.history.pop(0)
    
    @property
    def change_pct(self):
        if self.prev_price == 0:
            return 0.0
        return ((self.price - self.prev_price) / self.prev_price) * 100.0
    
    def trend_arrow(self):
        if self.change_pct > 5: return f"{C.GREEN}▲{C.END}"
        if self.change_pct > 0.5: return f"{C.GREEN}↑{C.END}"
        if self.change_pct < -5: return f"{C.RED}▼{C.END}"
        if self.change_pct < -0.5: return f"{C.RED}↓{C.END}"
        return f"{C.DIM}→{C.END}"

# ==================== JUGADOR ====================

class Player:
    def __init__(self):
        self.money = 2000.0
        self.portfolio = {}  # symbol -> qty
    
    def net_worth(self, market):
        total = self.money
        for sym, qty in self.portfolio.items():
            asset = market.assets.get(sym)
            if asset:
                total += qty * asset.price
        return total
    
    def has(self, symbol):
        return self.portfolio.get(symbol, 0)

# ==================== BOTS ====================

class Bot:
    def __init__(self, name, symbol, condition, action, amount):
        self.name = name
        self.symbol = symbol.upper()
        self.condition = condition.lower().replace(" ", "")
        self.action = action.lower()
        self.amount = amount  # int o "todo"
        self.active = True
        self.trades = 0
    
    def evaluate(self, market, player):
        asset = market.assets.get(self.symbol)
        if not asset:
            return False, "Activo inválido"
        
        triggered = False
        cond = self.condition
        
        if cond == "siempre":
            triggered = True
        elif cond == "sube":
            triggered = asset.price > asset.prev_price
        elif cond == "baja":
            triggered = asset.price < asset.prev_price
        elif cond.startswith("precio<"):
            try:
                val = float(cond.split("<")[1])
                triggered = asset.price < val
            except:
                triggered = False
        elif cond.startswith("precio>"):
            try:
                val = float(cond.split(">")[1])
                triggered = asset.price > val
            except:
                triggered = False
        else:
            return False, f"Condición '{cond}' no reconocida"
        
        if not triggered:
            return False, "Esperando condición"
        
        # Ejecutar
        if self.action == "comprar":
            qty = self.amount
            if qty == "todo":
                qty = int(player.money // asset.price)
            if qty <= 0:
                return False, "Sin fondos"
            cost = qty * asset.price
            if cost > player.money:
                return False, "Capital insuficiente"
            player.money -= cost
            player.portfolio[self.symbol] = player.portfolio.get(self.symbol, 0) + qty
            self.trades += 1
            return True, f"{C.GREEN}BOT {self.name}{C.END}: Compró {qty} {self.symbol} @ {asset.price:.2f}"
        
        elif self.action == "vender":
            qty = self.amount
            owned = player.portfolio.get(self.symbol, 0)
            if qty == "todo":
                qty = owned
            if qty <= 0 or owned <= 0:
                return False, "Sin activos"
            qty = min(qty, owned)
            gain = qty * asset.price
            player.money += gain
            player.portfolio[self.symbol] -= qty
            if player.portfolio[self.symbol] == 0:
                del player.portfolio[self.symbol]
            self.trades += 1
            return True, f"{C.RED}BOT {self.name}{C.END}: Vendió {qty} {self.symbol} @ {asset.price:.2f}"
        
        return False, "Acción desconocida"

# ==================== MERCADO ====================

class Market:
    ASSETS_DEF = [
        ("ESP", "Esperanza", 100.0, 0.04),
        ("PAT", "Patos NFT", 45.0, 0.10),
        ("AIR", "Aire Enlatado", 12.0, 0.03),
        ("MEM", "Memecoins", 3.5, 0.18),
        ("KAR", "Karma", 80.0, 0.06),
        ("SUE", "Sueños", 28.0, 0.09),
        ("DUD", "Dudas Existenciales", 15.0, 0.12),
        ("LUN", "Lunes", 8.0, 0.20),
    ]
    
    CLIMATES = [
        ("Soleado",           {'SUE': 0.02, 'ESP': 0.01}),
        ("Lluvioso",          {'DUD': 0.03, 'ESP': -0.02}),
        ("Tormenta de Memes", {'MEM': 0.08, 'PAT': 0.04}),
        ("Eclipse Existencial",{'KAR': 0.05, 'ESP': -0.05}),
        ("Lunes Perpetuo",    {'LUN': 0.12, 'SUE': -0.04, 'ESP': -0.03}),
        ("Arcoíris Tóxico",   {'AIR': 0.06, 'MEM': 0.03}),
        ("Calma Chicha",      {}),
    ]
    
    EVENTS = [
        ("Viral: Gato toca piano", {'MEM': 0.35, 'PAT': 0.08}),
        ("Escasez mundial de esperanza", {'ESP': 0.40, 'DUD': 0.15}),
        ("Patos conquistan TikTok", {'PAT': 0.28, 'MEM': 0.05}),
        ("Meme muere en trending", {'MEM': -0.40, 'KAR': -0.05}),
        ("Descubren aire en Marte", {'AIR': -0.20, 'ESP': 0.05}),
        ("Lunes fue cancelado", {'LUN': -0.35, 'ESP': 0.25, 'SUE': 0.10}),
        ("Revolución de los sueños", {'SUE': 0.30, 'DUD': -0.10}),
        ("Filósofo duda de los memes", {'MEM': -0.18, 'DUD': 0.22}),
        ("Inflación de patos", {'PAT': -0.22, 'AIR': 0.05}),
        ("Tormenta de ideas", {'SUE': 0.18, 'ESP': 0.12, 'KAR': 0.08}),
        ("Crisis de lunes", {'LUN': 0.30, 'ESP': -0.10}),
        ("NFT de pato vendido por millones", {'PAT': 0.35, 'MEM': 0.10}),
    ]
    
    def __init__(self):
        self.assets = {sym: Asset(sym, name, price, vol) for sym, name, price, vol in self.ASSETS_DEF}
        self.turn = 1
        self.climate = self.CLIMATES[0]
        self.last_event = None
        self.bots = []
        self.logs = []
        self.player = Player()
    
    def climate_mod(self, symbol):
        return self.climate[1].get(symbol, 0.0)
    
    def next_turn(self):
        self.turn += 1
        # Cambio de clima
        if random.random() < 0.25:
            self.climate = random.choice(self.CLIMATES)
        
        # Evento aleatorio
        event_mods = {}
        self.last_event = None
        if random.random() < 0.45:
            name, mods = random.choice(self.EVENTS)
            self.last_event = name
            event_mods = mods
        
        # Fluctuar precios
        for sym, asset in self.assets.items():
            asset.fluctuate(event_mods.get(sym, 0.0), self.climate_mod(sym))
        
        # Bots actúan
        bot_reports = []
        for bot in self.bots:
            if bot.active:
                ok, msg = bot.evaluate(self, self.player)
                if ok:
                    bot_reports.append(msg)
        
        # Logging
        if self.last_event:
            self.logs.append(f"{C.MAGENTA}EVENTO: {self.last_event}{C.END}")
        self.logs.append(f"{C.BLUE}Clima: {self.climate[0]}{C.END}")
        for r in bot_reports:
            self.logs.append(r)
        if len(self.logs) > 12:
            self.logs = self.logs[-12:]

# ==================== RENDER ====================

def render(market):
    clear()
    print(f"{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════════════════╗{C.END}")
    print(f"{C.CYAN}{C.BOLD}║{C.END}  📈 MERCADO CAÓTICO  —  Turno {market.turn:<4}  —  {C.YELLOW}{market.climate[0]}{C.END}{' '*18}{C.CYAN}{C.BOLD}║{C.END}")
    print(f"{C.CYAN}{C.BOLD}╠══════════════════════════════════════════════════════════════════════╣{C.END}")
    
    # Tabla de precios
    print(f"  {C.BOLD}{'Símb':<6} {'Nombre':<22} {'Precio':>10} {'Cambio':>10} {'Tend':>6}{C.END}")
    print(f"  {'-'*58}")
    for sym, asset in market.assets.items():
        color = C.GREEN if asset.change_pct >= 0 else C.RED
        sign = "+" if asset.change_pct >= 0 else ""
        print(f"  {C.BOLD}{sym:<6}{C.END} {asset.name:<22} {asset.price:>10.2f} {color}{sign}{asset.change_pct:>8.1f}%{C.END} {asset.trend_arrow():>6}")
    
    # Evento actual
    if market.last_event:
        print(f"\n  {C.MAGENTA}⚡ {market.last_event}{C.END}")
    
    # Cartera
    print(f"\n  {C.BOLD}{C.YELLOW}💰 Capital: ${market.player.money:,.2f}  |  💎 Patrimonio: ${market.player.net_worth(market):,.2f}{C.END}")
    if market.player.portfolio:
        print(f"  {C.BOLD}Posiciones:{C.END}")
        for sym, qty in sorted(market.player.portfolio.items()):
            val = qty * market.assets[sym].price
            print(f"     {sym}: {qty} unid.  (Valor: ${val:,.2f})")
    else:
        print(f"  {C.DIM}Sin posiciones abiertas.{C.END}")
    
    # Bots
    if market.bots:
        print(f"\n  {C.BOLD}🤖 Bots activos:{C.END}")
        for b in market.bots:
            status = f"{C.GREEN}ON{C.END}" if b.active else f"{C.RED}OFF{C.END}"
            amt = str(b.amount)
            print(f"     {status} {b.name}: {b.symbol} | {b.condition} → {b.action} {amt} (trades: {b.trades})")
    
    # Logs
    if market.logs:
        print(f"\n  {C.BOLD}{C.WHITE}─── ÚLTIMAS NOVEDADES ───{C.END}")
        for entry in market.logs[-6:]:
            print(f"  {entry}")
    
    print(f"\n  {C.DIM}Comandos: [Enter]=siguiente turno | comprar/vender <SYM> <cant> | bot <nombre> <SYM> <cond> <acc> <cant>")
    print(f"           bots | delbot <nombre> | cartera | ayuda | salir{C.END}")

# ==================== COMANDOS ====================

def cmd_buy(market, args):
    if len(args) < 2:
        print(f"{C.RED}Uso: comprar <SÍMBOLO> <CANTIDAD>{C.END}")
        return
    sym = args[0].upper()
    try:
        qty = int(args[1])
    except ValueError:
        if args[1].lower() == "todo":
            qty = "todo"
        else:
            print(f"{C.RED}Cantidad inválida.{C.END}")
            return
    
    asset = market.assets.get(sym)
    if not asset:
        print(f"{C.RED}Activo no existe.{C.END}")
        return
    
    if qty == "todo":
        qty = int(market.player.money // asset.price)
    if qty <= 0:
        print(f"{C.RED}Sin fondos suficientes.{C.END}")
        return
    
    cost = qty * asset.price
    if cost > market.player.money:
        print(f"{C.RED}Capital insuficiente. Necesitas ${cost:,.2f}, tienes ${market.player.money:,.2f}{C.END}")
        return
    
    market.player.money -= cost
    market.player.portfolio[sym] = market.player.portfolio.get(sym, 0) + qty
    market.logs.append(f"{C.GREEN}TÚ: Compraste {qty} {sym} @ {asset.price:.2f} (-${cost:,.2f}){C.END}")

def cmd_sell(market, args):
    if len(args) < 2:
        print(f"{C.RED}Uso: vender <SÍMBOLO> <CANTIDAD>{C.END}")
        return
    sym = args[0].upper()
    owned = market.player.portfolio.get(sym, 0)
    if owned <= 0:
        print(f"{C.RED}No posees {sym}.{C.END}")
        return
    
    try:
        qty = int(args[1])
    except ValueError:
        if args[1].lower() == "todo":
            qty = "todo"
        else:
            print(f"{C.RED}Cantidad inválida.{C.END}")
            return
    
    asset = market.assets.get(sym)
    if qty == "todo":
        qty = owned
    qty = min(qty, owned)
    
    gain = qty * asset.price
    market.player.money += gain
    market.player.portfolio[sym] -= qty
    if market.player.portfolio[sym] == 0:
        del market.player.portfolio[sym]
    market.logs.append(f"{C.RED}TÚ: Vendiste {qty} {sym} @ {asset.price:.2f} (+${gain:,.2f}){C.END}")

def cmd_bot(market, args):
    # bot <nombre> <simbolo> <condicion> <accion> <cantidad>
    if len(args) < 5:
        print(f"{C.RED}Uso: bot <nombre> <SÍMBOLO> <condición> <acción> <cantidad>{C.END}")
        print(f"  Condiciones: precio<50 | precio>100 | sube | baja | siempre")
        print(f"  Acciones: comprar | vender")
        print(f"  Cantidad: número o 'todo'")
        print(f"  Ejemplo: bot acumulador ESP precio<90 comprar 5")
        return
    
    name = args[0]
    sym = args[1].upper()
    cond = args[2]
    action = args[3].lower()
    amount = args[4].lower()
    
    if sym not in market.assets:
        print(f"{C.RED}Activo {sym} no existe.{C.END}")
        return
    if action not in ("comprar", "vender"):
        print(f"{C.RED}Acción debe ser 'comprar' o 'vender'.{C.END}")
        return
    if amount != "todo":
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            print(f"{C.RED}Cantidad debe ser número positivo o 'todo'.{C.END}")
            return
    
    # Verificar nombre único
    if any(b.name == name for b in market.bots):
        print(f"{C.RED}Ya existe un bot llamado '{name}'.{C.END}")
        return
    
    bot = Bot(name, sym, cond, action, amount)
    market.bots.append(bot)
    print(f"{C.GREEN}✓ Bot '{name}' desplegado.{C.END}")

def cmd_delbot(market, args):
    if not args:
        print(f"{C.RED}Uso: delbot <nombre>{C.END}")
        return
    name = args[0]
    market.bots = [b for b in market.bots if b.name != name]
    print(f"{C.YELLOW}Bot '{name}' eliminado.{C.END}")

def cmd_bots(market):
    if not market.bots:
        print(f"{C.DIM}No hay bots activos.{C.END}")
        return
    print(f"{C.BOLD}{'Nombre':<15} {'Act':<6} {'Condición':<15} {'Acción':<10} {'Cant':<8} {'Trades':<6}{C.END}")
    for b in market.bots:
        a = "ON" if b.active else "OFF"
        print(f"{b.name:<15} {a:<6} {b.condition:<15} {b.action:<10} {str(b.amount):<8} {b.trades:<6}")

def cmd_portfolio(market):
    print(f"\n{C.BOLD}CARTERA DETALLADA{C.END}")
    print(f"Efectivo: ${market.player.money:,.2f}")
    total = market.player.money
    for sym, qty in sorted(market.player.portfolio.items()):
        asset = market.assets[sym]
        val = qty * asset.price
        total += val
        print(f"  {sym} ({asset.name}): {qty} @ {asset.price:.2f} = ${val:,.2f}")
    print(f"{C.BOLD}Patrimonio neto: ${total:,.2f}{C.END}")

def cmd_help():
    print(f"""
{C.CYAN}{C.BOLD}═══════════════════════════════════════════════════════════════{C.END}
  {C.BOLD}COMANDOS DISPONIBLES{C.END}

  {C.GREEN}[Enter]{C.END}              Avanzar al siguiente turno
  {C.GREEN}comprar <S> <N>{C.END}    Comprar N unidades del activo S
  {C.GREEN}vender <S> <N>{C.END}     Vender N unidades (o 'todo')
  {C.GREEN}bot <n> <S> <c> <a> <N>{C.END}  Crear bot automático
  {C.GREEN}bots{C.END}               Listar bots activos
  {C.GREEN}delbot <nombre>{C.END}   Eliminar un bot
  {C.GREEN}cartera{C.END}            Ver detalle de posesiones
  {C.GREEN}ayuda{C.END}              Mostrar esta ayuda
  {C.GREEN}salir{C.END}              Abandonar el mercado

{C.CYAN}{C.BOLD}═══════════════════════════════════════════════════════════════{C.END}
  {C.BOLD}SINTAXIS DE BOTS{C.END}

  bot <nombre> <símbolo> <condición> <acción> <cantidad>

  {C.YELLOW}Condiciones:{C.END}
    precio<50       Actuar si precio < 50
    precio>200      Actuar si precio > 200
    sube            Actuar si el precio subió este turno
    baja            Actuar si el precio bajó este turno
    siempre         Actuar cada turno

  {C.YELLOW}Ejemplos:{C.END}
    bot lowbuy ESP precio<80 comprar 10
    bot panic MEM precio<2 vender todo
    bot always LUN siempre comprar 1
""")

# ==================== MAIN ====================

def main():
    clear()
    print(f"""{C.CYAN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     S I M U L A D O R   D E   M E R C A D O   C A Ó T I C O   ║
    ║                                                               ║
    ║  Bienvenido al exchange más absurdo del multiverso.           ║
    ║  Aquí se comercia Esperanza, Patos NFT y Aire Enlatado.       ║
    ║  El clima decide tendencias. Los memes mueven mercados.       ║
    ║  Despliega bots. Hazte rico. O no.                            ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    {C.END}""")
    input(f"{C.DIM}Presiona Enter para abrir la sesión de trading...{C.END}")
    
    market = Market()
    
    while True:
        render(market)
        
        try:
            cmd_line = input(f"\n{C.BOLD}> {C.END}").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not cmd_line:
            market.next_turn()
            continue
        
        parts = cmd_line.split()
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in ("comprar", "buy"):
            cmd_buy(market, args)
            input(f"{C.DIM}Enter para continuar...{C.END}")
        elif cmd in ("vender", "sell"):
            cmd_sell(market, args)
            input(f"{C.DIM}Enter para continuar...{C.END}")
        elif cmd == "bot":
            cmd_bot(market, args)
            input(f"{C.DIM}Enter para continuar...{C.END}")
        elif cmd == "bots":
            cmd_bots(market)
            input(f"{C.DIM}Enter para continuar...{C.END}")
        elif cmd == "delbot":
            cmd_delbot(market, args)
            input(f"{C.DIM}Enter para continuar...{C.END}")
        elif cmd in ("cartera", "portfolio", "p"):
            cmd_portfolio(market)
            input(f"{C.DIM}Enter para continuar...{C.END}")
        elif cmd in ("ayuda", "help"):
            cmd_help()
            input(f"{C.DIM}Enter para continuar...{C.END}")
        elif cmd in ("salir", "exit", "quit"):
            print(f"{C.YELLOW}Cerrando sesión. Que los memes te acompañen.{C.END}")
            break
        else:
            print(f"{C.RED}Comando no reconocido: '{cmd}'. Escribe 'ayuda'.{C.END}")
            input(f"{C.DIM}Enter para continuar...{C.END}")

if __name__ == "__main__":
    main()
