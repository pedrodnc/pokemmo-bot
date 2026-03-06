# Libs
import os
import platform
import json

# AlphaForny Core
from AlphaForny import AlphaForny

# Language
from Language import Language
from Translator import Translator

# Config Setup
from Config import Config
config = Config()

STARTDIR = config.general['STARTDIR']

# Utils
from utils import Clear
clear = Clear(False)

# Language Setup
# language = Language(STARTDIR, clear)          [ DEBUG ]
# lang = language.chooseLang()                  [ DEBUG ]
with open('./lang/en.json') as f:
    translator = Translator(json.load(f))
t = translator.t

# Script Setup
from Script import Script
def loadScript():
    chose = None
    script = Script(STARTDIR, 'scripts', t, clear)

    while (chose == None):
        script.printCurrDir()
        if (not script.isStart()):
            print(t('main.goback'), -1)
        idx = int(input(f'{ t("main.select2") }: '))
        
        if (idx >= 0):
            item = script.idxItemToPath(idx)
            if (item == None):
                continue
            elif (os.path.isdir(item)):
                script.gotoDir(idx)
            else:
                chose = item
        elif (idx == -1):
            script.backDir()
    return chose

if __name__ == "__main__":
    # Cambia esta ruta para usar otro script:
    # Route 3 desde Striaton City (gym 1 completado, sin HMs):
    scriptPath = './scripts/Exp/Route3_Striaton.txt'
    # Route 2 desde Accumula Town (inicio del juego):
    # scriptPath = './scripts/Exp/Route2_EarlyUnova.txt'
    # Spiraria (requiere HM Surf, mid-late game):
    # scriptPath = './scripts/Exp/Spiraria.txt'
    alphaForny = AlphaForny(scriptPath, t, clear)
    alphaForny.start()