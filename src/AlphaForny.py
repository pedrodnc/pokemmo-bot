import time

from FornyTranslator import FornyTranslator
from Action import Action
from Config import Config

from pynput.keyboard import Key, Listener
from threading import Thread


class AlphaForny(FornyTranslator, Action):
    def __init__(self, scriptPath, t, clear) -> None:
        try:
            cfg = Config()
            game_cfg = getattr(cfg, 'game', {})
            safety_cfg = getattr(cfg, 'safety', {})
            window_title = game_cfg.get('WINDOW_TITLE', 'PokeMMO')
            auto_focus = safety_cfg.get('AUTO_FOCUS', True)
        except Exception:
            window_title = 'PokeMMO'
            auto_focus = True

        self.action = Action(
            window_title=window_title,
            auto_focus=auto_focus,
        )
        self.t = t
        self.clear = clear

        super().__init__(scriptPath, self.action, self.t, self.clear)

        self.pause = False
        self.end = False
        self.run = False
        self.bike = False

    def onPress(self, key):
        pass

    def onRelease(self, key):
        try:
            if key == Key.esc:
                print(f"[{self.t('general.status.state')}]: {self.t('alphaforny.killed')}")
                self._printStats()
                self.end = True
                return False
            elif key.char == 'p':
                if not self.pause:
                    print(f"[{self.t('general.status.state')}]: {self.t('alphaforny.paused')}")
                    self.pause = True
                else:
                    print(f"[{self.t('general.status.state')}]: {self.t('alphaforny.resumed')}")
                    self.pause = False
        except AttributeError:
            pass
        except Exception as err:
            print(f'[{self.t("general.status.state")}]: {self.t("alphaforny.handling_error")}')
            print(err)

    def _printStats(self):
        """Imprime estadisticas de la sesion."""
        elapsed = (time.time() - self.session_start) / 60
        bph = (self.total_battles / elapsed * 60) if elapsed > 0 else 0
        print(f'[STATS] {self.total_battles} batallas en {elapsed:.1f} min ({bph:.0f}/hora)')
        if self.ai_agent:
            stats = self.ai_agent.get_stats()
            print(f'[STATS] IA: {stats["calls"]} llamadas API')

    def exec(self, skipStart=False):
        self.action.focusWindow()

        if not skipStart:
            for instruction in self.cmds:
                if instruction != 'loop':
                    for cmd in self.cmds[instruction]:
                        while self.pause:
                            pass
                        if type(cmd) is dict:
                            key, value = next(iter(cmd.items()))
                            self.translateCmd(key, value)
                        else:
                            self.translateCmd(cmd)

        while not self.end:
            # Verificar limite de sesion
            if self.checkSessionLimit():
                self.end = True
                break

            # Pausa anti-deteccion
            self.maybeAFKPause()

            # Reset para nuevo loop
            self.battle_handled = False
            self.battles_this_loop = 0
            self.loop_count += 1

            for cmd in self.cmds['loop']:
                while self.pause:
                    pass
                if self.end:
                    break
                if type(cmd) is dict:
                    key, value = next(iter(cmd.items()))
                    self.translateCmd(key, value)
                else:
                    self.translateCmd(cmd)

        self._printStats()

    def start(self):
        print(f"[{self.t('general.status.state')}]: {self.t('alphaforny.start')}")
        print(f'[CONFIG] Batallas/heal: {self.battles_per_heal} | Patron: {self.walk_pattern} | Jitter: ±{int(self.sleep_jitter*100)}%')
        if self.ai_agent:
            print(f'[CONFIG] IA activa: {self.ai_agent.model}')
        if self.session_max > 0:
            print(f'[CONFIG] Sesion max: {self.session_max} min')
        if self.afk_pause_every > 0:
            print(f'[CONFIG] Pausa AFK cada {self.afk_pause_every} loops')

        executeThread = Thread(target=self.exec, args=(False,), daemon=True)
        executeThread.start()

        with Listener(
            on_press=self.onPress,
            on_release=self.onRelease) as listener:
            listener.join()
