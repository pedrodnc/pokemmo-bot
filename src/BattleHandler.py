import time

from pynput.keyboard import Key


class BattleHandler:
    """Maneja la logica de batalla: seleccion de movimiento, captura, whiteout.

    Layout del menu de batalla PokéMMO (2x2):
      [Fight]   [Bag]
      [Pokemon] [Run]

    Layout de movimientos (2x2):
      [Move1] [Move2]
      [Move3] [Move4]
    """

    MOVE_NAV = {
        1: [],
        2: [Key.right],
        3: [Key.down],
        4: [Key.right, Key.down],
    }

    def __init__(self, action, action_key='z', back_key='x',
                 move_slot=1, auto_catch=False):
        self.action = action
        self.action_key = action_key
        self.back_key = back_key
        self.move_slot = move_slot
        self.auto_catch = auto_catch

    def _press(self, key):
        """Press a key using pynput Key or char string."""
        if isinstance(key, str):
            self.action.pressKey(key)
        else:
            self.action.pressKey(key)

    def select_move(self, slot):
        """Navega al slot de movimiento indicado (1-4) en el menu 2x2."""
        nav = self.MOVE_NAV.get(slot, [])
        for key in nav:
            self._press(key)
            time.sleep(0.15)

    def fight_turn(self):
        """Ejecuta un turno: Fight → navegar al movimiento → confirmar."""
        # "Fight" ya esta seleccionado por defecto
        self._press(self.action_key)
        time.sleep(0.4)

        # Navegar al movimiento configurado
        self.select_move(self.move_slot)
        time.sleep(0.2)

        # Confirmar movimiento
        self._press(self.action_key)

    def attempt_catch(self):
        """Intenta capturar: Fight→Bag (derecha) → Pokeball → confirmar."""
        # Desde el menu de batalla, navegar a "Bag" (derecha de Fight)
        self._press(Key.right)
        time.sleep(0.3)
        self._press(self.action_key)
        time.sleep(0.8)

        # Seleccionar primera Pokeball del inventario
        self._press(self.action_key)
        time.sleep(0.3)
        self._press(self.action_key)

    def do_battle(self, wait_fn, timeout=120):
        """Ejecuta batalla completa hasta volver al mapa.

        Args:
            wait_fn: funcion waitFor del Action (what, timeout=)
            timeout: timeout maximo para la batalla entera
        """
        if self.auto_catch:
            # Intentar capturar primero
            self.attempt_catch()
            time.sleep(2)
            # Si no se capturo, el juego vuelve al menu de batalla
            # Verificar si seguimos en batalla
            if self.action.checkBattle():
                # No se capturo, pelear normalmente
                self.fight_turn()
                time.sleep(0.5)
        else:
            # Seleccionar movimiento configurado
            self.fight_turn()
            time.sleep(0.5)

        # Spam action key para pasar dialogos restantes (XP, level up, etc.)
        self.action.createSpam(self.action_key)
        wait_fn('terrain', timeout=timeout)
        self.action.destroySpam()
        time.sleep(0.5)

    def check_whiteout(self):
        """Detecta whiteout: tras batalla, si vemos el interior del centro
        en vez del terreno de ruta, hubo whiteout."""
        # Tras whiteout el juego te pone dentro del centro Pokemon.
        # Buscamos si 'terrain' NO aparece rapido (ya que estamos dentro).
        # Si 'center' aparece de inmediato = estamos frente al centro = normal.
        # Si ninguno aparece = podriamos estar dentro del centro (whiteout).
        return False  # TODO: necesita ref de interior de centro para ser fiable
