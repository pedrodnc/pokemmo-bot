# Automate APIs
import pyautogui as pag

# Input APIs
import pynput.mouse as mouse
import pynput.keyboard as kbd

from pynput.mouse import Button
from pynput.keyboard import Key

import time
from threading import Thread

# Windows-only: auto-focus de ventana
try:
    import ctypes
    _user32 = ctypes.windll.user32
    HAS_WIN32 = True
except (ImportError, AttributeError):
    HAS_WIN32 = False


class Action:
    def __init__(self, confidence=.85, window_title="PokeMMO", auto_focus=True) -> None:
        self.confidence = confidence
        self.window_title = window_title
        self.auto_focus = auto_focus

        self.mouse = mouse.Controller()
        self.kbd = kbd.Controller()

        self.spam = False

    def focusWindow(self):
        """Trae la ventana de PokéMMO al frente (solo Windows)."""
        if not HAS_WIN32 or not self.auto_focus:
            return False
        try:
            hwnd = _user32.FindWindowW(None, self.window_title)
            if hwnd:
                _user32.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                return True
        except Exception:
            pass
        return False

    def clickTo(self, x, y, left=True, sleep1=.1, sleep2=.5):
        self.focusWindow()
        self.mouse.position = (x, y)
        self.mouse.press(Button.left if left else Button.right)
        time.sleep(sleep1)
        self.mouse.release(Button.left if left else Button.right)
        time.sleep(sleep2)

    def isOnScreen(self, what) -> bool:
        try:
            return pag.locateOnScreen(
                f'./refs/{what}.png',
                grayscale=False,
                confidence=self.confidence
            ) is not None
        except pag.ImageNotFoundException:
            return False
        except Exception:
            return False

    def checkBattle(self) -> bool:
        return self.isOnScreen('lotta')

    def waitFor(self, what, until=False, sleep=.1, timeout=None):
        elapsed = 0
        while True:
            if until and (not self.isOnScreen(what)):
                break
            elif not until and self.isOnScreen(what):
                break
            time.sleep(sleep)
            elapsed += sleep
            if timeout and elapsed >= timeout:
                print(f'[TIMEOUT] waitFor {what} tras {timeout}s')
                break

    def holdKey(self, key):
        self.kbd.press(key)

    def releaseKey(self, key):
        self.kbd.release(key)

    def pressKey(self, key, sleep1=.1, sleep2=.2):
        self.holdKey(key)
        time.sleep(sleep1)
        self.releaseKey(key)
        time.sleep(sleep2)

    def spamKey(self, key, sleep1=.1, sleep2=.2, sleep3=.5):
        while self.spam:
            self.pressKey(key, sleep1, sleep2)
            time.sleep(sleep3)

    def createSpam(self, key, sleep1=.1, sleep2=.2, sleep3=.5):
        self.spam = True
        spamThread = Thread(target=self.spamKey, args=(key, sleep1, sleep2, sleep3))
        spamThread.start()

    def destroySpam(self):
        self.spam = False
