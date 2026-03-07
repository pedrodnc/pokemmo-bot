import time
import random

from pynput.keyboard import Key

from Config import Config
from BattleHandler import BattleHandler


class FornyTranslator:
    def __init__(self, scriptPath, action, t, clear) -> None:
        self.scriptPath = scriptPath
        self.actions = action
        self.t = t
        self.clear = clear
        self.battle_handled = False
        self.battles_this_loop = 0
        self.total_battles = 0
        self.loop_count = 0

        # Leer config
        try:
            cfg = Config()
        except Exception:
            cfg = None

        # Safety
        safety_cfg = getattr(cfg, 'safety', {}) if cfg else {}
        self.sleep_jitter = safety_cfg.get('SLEEP_JITTER', 0.2)
        self.waitfor_timeout = safety_cfg.get('WAITFOR_TIMEOUT', 120)
        self.afk_pause_every = safety_cfg.get('AFK_PAUSE_EVERY', 0)
        self.session_max = safety_cfg.get('SESSION_MAX_MINUTES', 0)

        # Walk
        walk_cfg = getattr(cfg, 'walk', {}) if cfg else {}
        self.walk_pattern = walk_cfg.get('PATTERN', 'zigzag')
        self.walk_step_duration = walk_cfg.get('STEP_DURATION', 1.5)
        self.walk_steps = walk_cfg.get('STEPS', 6)

        # Battle
        battle_cfg = getattr(cfg, 'battle', {}) if cfg else {}
        controls_cfg = getattr(cfg, 'controls', {}) if cfg else {}
        self.battles_per_heal = battle_cfg.get('BATTLES_PER_HEAL', 5)
        self.battle_handler = BattleHandler(
            action=action,
            action_key=controls_cfg.get('ACTION_KEY', 'z'),
            back_key=controls_cfg.get('BACK_KEY', 'x'),
            move_slot=battle_cfg.get('MOVE_SLOT', 1),
            auto_catch=battle_cfg.get('AUTO_CATCH', False),
        )

        # AI agent (opcional)
        self.ai_agent = None
        ai_cfg = getattr(cfg, 'ai', {}) if cfg else {}
        if ai_cfg.get('ENABLED', False):
            try:
                from AIAgent import AIAgent
                self.ai_agent = AIAgent(
                    model=ai_cfg.get('MODEL', 'claude-haiku-4-5-20251001'),
                    check_interval=ai_cfg.get('CHECK_INTERVAL', 10),
                )
                print('[AI] Agente IA activado')
            except Exception as e:
                print(f'[AI] No se pudo iniciar: {e}')

        self.session_start = time.time()
        self.cmds = self.getCmds()

    # --- Parser ---

    def normalizeRow(self, row):
        if row.find('#') >= 0:
            return row.strip()[: -(len(row) - row.find('#'))]
        else:
            return row.strip()

    def getCmds(self):
        with open(self.scriptPath, 'r') as f:
            lines = f.readlines()

        cmds = {}
        lastCmd = ""

        try:
            for line in lines:
                normalizedLine = self.normalizeRow(line)
                if len(normalizedLine) <= 0:
                    pass
                elif normalizedLine.find(':') >= 0:
                    lastCmd = normalizedLine[: -(len(normalizedLine) - normalizedLine.find(':'))]
                    cmds[lastCmd] = []
                else:
                    splittedLine = normalizedLine.split()
                    if len(splittedLine) > 1:
                        if splittedLine[1].find(',') >= 0:
                            splittedLine[1] = splittedLine[1].split(',')
                        key, value = splittedLine[:2]
                        if not self.validateCmd(key, value):
                            raise Exception(f'{key} {value} {self.t("translator.notvalid")}')
                        cmds[lastCmd].append({key: value})
                    else:
                        if not self.validateCmd(splittedLine[0]):
                            raise Exception(f'{splittedLine[0]} {self.t("translator.notvalid")}')
                        cmds[lastCmd].append(splittedLine[0])
        except Exception as err:
            self.clear.clearScreen()
            print(f'[{self.t("general.status.error")}]:', err)
        return cmds

    def mapKey(self, key):
        if key == 'UP':
            return Key.up
        elif key == 'DOWN':
            return Key.down
        elif key == 'RIGHT':
            return Key.right
        elif key == 'LEFT':
            return Key.left
        elif key == 'SHIFT':
            return Key.shift
        elif type(key) is str:
            return key.lower()
        return None

    def validateCmd(self, key, value=None):
        try:
            valid_cmds = {
                'CLICK': lambda: type(value) is list and len(value) > 1,
                'SLEEP': lambda: type(float(value)) is float,
                'WAITFOR': lambda: type(value) is str,
                'PRINT': lambda: type(value) is str,
                'WAITBATTLE': lambda: value is None,
                'SKIP': lambda: value is None,
                'PRESS': lambda: type(value) is str and self.mapKey(value) is not None,
                'HOLD': lambda: type(value) is str and self.mapKey(value) is not None,
                'RELEASE': lambda: type(value) is str and self.mapKey(value) is not None,
                'SPAM': lambda: type(value) is str and self.mapKey(value) is not None,
                'STOPSPAM': lambda: type(value) is str and self.mapKey(value) is not None,
                'UNTIL': lambda: type(value) is str,
                'WALK': lambda: type(value) is str and value in ('zigzag', 'circle', 'random', 'leftright', 'updown'),
                'FISH': lambda: type(value) is str,
            }
            if key in valid_cmds:
                return valid_cmds[key]()
            return False
        except:
            return False

    # --- Battle ---

    def doBattle(self):
        """Ejecuta batalla completa usando BattleHandler."""
        self.battles_this_loop += 1
        self.total_battles += 1
        print(f'[BATTLE] #{self.total_battles} (ciclo: {self.battles_this_loop}/{self.battles_per_heal})')
        self.battle_handled = True
        self.actions.focusWindow()
        self.battle_handler.do_battle(
            wait_fn=self.actions.waitFor,
            timeout=self.waitfor_timeout
        )
        print(f'[BATTLE] Terminada')

    def shouldHeal(self):
        """Decide si hay que volver al centro a curar."""
        # Por contador
        if self.battles_this_loop >= self.battles_per_heal:
            return True
        # Por IA (si disponible)
        if self.ai_agent:
            try:
                if self.ai_agent.needs_heal():
                    print('[AI] IA recomienda curar')
                    return True
            except Exception:
                pass
        return False

    # --- Walk patterns ---

    def _battleCheckSleep(self, duration):
        """Sleep que checkea batalla cada 0.5s."""
        step = 0.1
        elapsed = 0
        next_check = 0.5
        while elapsed < duration:
            time.sleep(min(step, duration - elapsed))
            elapsed += step
            if elapsed >= next_check:
                next_check += 0.5
                if not self.battle_handled and self.actions.checkBattle():
                    for k in [Key.up, Key.down, Key.left, Key.right]:
                        try:
                            self.actions.releaseKey(k)
                        except Exception:
                            pass
                    self.doBattle()
                    break

    def _doWalkCycle(self, pattern, step_dur, steps, dirs):
        """Ejecuta un ciclo de movimiento completo."""
        for i in range(steps):
            if self.battle_handled:
                break

            if pattern == 'random':
                direction = random.choice([Key.up, Key.down, Key.left, Key.right])
            else:
                direction = dirs[i % len(dirs)]

            self.actions.holdKey(direction)
            self._battleCheckSleep(step_dur)
            if not self.battle_handled:
                self.actions.releaseKey(direction)
            time.sleep(random.uniform(0.15, 0.3))

    def executeWalk(self, pattern=None):
        """Ejecuta multiples ciclos de movimiento hasta alcanzar BATTLES_PER_HEAL.

        Repite el patron de caminar hasta que:
        - Se alcanzan N batallas (BATTLES_PER_HEAL)
        - O la IA dice que hay que curar
        Esto reduce drasticamente las visitas al centro."""
        pattern = pattern or self.walk_pattern
        step_dur = self.walk_step_duration
        steps = self.walk_steps

        if pattern == 'leftright':
            dirs = [Key.left, Key.right]
        elif pattern == 'updown':
            dirs = [Key.up, Key.down]
        elif pattern == 'circle':
            dirs = [Key.up, Key.right, Key.down, Key.left]
        elif pattern == 'random':
            dirs = None
        else:  # zigzag
            dirs = [Key.right, Key.down, Key.left, Key.up]

        self.actions.focusWindow()

        while not self.shouldHeal():
            self.battle_handled = False
            self._doWalkCycle(pattern, step_dur, steps, dirs)

            if not self.battle_handled:
                # No hubo batalla en este ciclo, esperar una
                self.actions.waitFor('lotta', timeout=self.waitfor_timeout)
                if self.actions.checkBattle():
                    self.doBattle()

            time.sleep(random.uniform(0.3, 0.8))

        # Señalar que la batalla se manejo (para que el script salte WAITFOR/SPAM)
        self.battle_handled = True

    # --- Fish ---

    def executeFish(self, rod_key='4'):
        """Ciclo de pesca: lanzar caña → esperar picada → pelear."""
        self.actions.focusWindow()
        self.actions.pressKey(rod_key)
        time.sleep(1.5)
        self.actions.waitFor('excl', timeout=30)
        time.sleep(0.2)
        self.actions.pressKey(self.mapKey(self.battle_handler.action_key))
        time.sleep(0.5)
        self.actions.waitFor('lotta', timeout=15)
        if self.actions.checkBattle():
            self.doBattle()

    # --- Anti-deteccion ---

    def maybeAFKPause(self):
        """Pausa aleatoria larga para simular comportamiento humano."""
        if self.afk_pause_every <= 0:
            return
        if self.loop_count > 0 and self.loop_count % self.afk_pause_every == 0:
            pause = random.uniform(30, 120)
            print(f'[AFK] Pausa anti-deteccion: {pause:.0f}s')
            time.sleep(pause)

    def checkSessionLimit(self):
        """Verifica si la sesion excedio el tiempo maximo."""
        if self.session_max <= 0:
            return False
        elapsed = (time.time() - self.session_start) / 60
        if elapsed >= self.session_max:
            print(f'[SESSION] Limite de {self.session_max} min alcanzado ({self.total_battles} batallas)')
            return True
        return False

    # --- Command execution ---

    def translateCmd(self, key, value=None):
        if key == 'CLICK':
            clickX, clickY = map(int, value[:2])
            self.actions.clickTo(clickX, clickY)

        elif key == 'SLEEP':
            base = float(value)
            jitter = base * self.sleep_jitter
            duration = random.uniform(base - jitter, base + jitter)
            if not self.battle_handled and base >= 0.5:
                self._battleCheckSleep(duration)
            else:
                time.sleep(duration)

        elif key == 'WAITFOR':
            if value in ('lotta', 'terrain') and self.battle_handled:
                return
            self.actions.waitFor(value, timeout=self.waitfor_timeout)

        elif key == 'PRINT':
            print(value)

        elif key == 'PRESS':
            self.actions.pressKey(self.mapKey(value))

        elif key == 'HOLD':
            self.actions.holdKey(self.mapKey(value))

        elif key == 'RELEASE':
            self.actions.releaseKey(self.mapKey(value))

        elif key == 'SPAM':
            if not self.battle_handled:
                self.actions.createSpam(self.mapKey(value))

        elif key == 'STOPSPAM':
            if not self.battle_handled:
                self.actions.destroySpam()

        elif key == 'UNTIL':
            self.actions.waitFor(value, until=True, timeout=self.waitfor_timeout)

        elif key == 'WALK':
            self.executeWalk(pattern=value)

        elif key == 'FISH':
            self.executeFish(rod_key=value)
