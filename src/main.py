# Libs
import os
import json

# Config Setup
from Config import Config
config = Config()

STARTDIR = config.general['STARTDIR']

# Language
from Translator import Translator
with open('./lang/en.json') as f:
    translator = Translator(json.load(f))
t = translator.t

# Utils
from utils import Clear
clear = Clear(False)


def loadScript():
    from Script import Script
    chose = None
    script = Script(STARTDIR, 'scripts', t, clear)

    while chose is None:
        script.printCurrDir()
        if not script.isStart():
            print(t('main.goback'), -1)
        idx = int(input(f'{t("main.select2")}: '))

        if idx >= 0:
            item = script.idxItemToPath(idx)
            if item is None:
                continue
            elif os.path.isdir(item):
                script.gotoDir(idx)
            else:
                chose = item
        elif idx == -1:
            script.backDir()
    return chose


def run_script_mode():
    """Modo normal: ejecuta un script .txt"""
    from AlphaForny import AlphaForny

    bot_cfg = getattr(config, 'bot', {})
    scriptPath = bot_cfg.get('SCRIPT', './scripts/Exp/Route3_Striaton.txt')

    if not os.path.isfile(scriptPath):
        print(f'[ERROR] Script no encontrado: {scriptPath}')
        scriptPath = loadScript()

    print(f'[BOT] Script: {scriptPath}')
    alphaForny = AlphaForny(scriptPath, t, clear)
    alphaForny.start()


def run_agent_mode():
    """Modo agente IA: toma decisiones por screenshot + Claude API"""
    from Action import Action
    from BattleHandler import BattleHandler
    from AIAgent import AIAgent, AIAutonomousAgent

    game_cfg = getattr(config, 'game', {})
    safety_cfg = getattr(config, 'safety', {})
    ai_cfg = getattr(config, 'ai', {})
    controls_cfg = getattr(config, 'controls', {})
    battle_cfg = getattr(config, 'battle', {})

    action = Action(
        window_title=game_cfg.get('WINDOW_TITLE', 'PokeMMO'),
        auto_focus=safety_cfg.get('AUTO_FOCUS', True),
    )

    battle_handler = BattleHandler(
        action=action,
        action_key=controls_cfg.get('ACTION_KEY', 'z'),
        back_key=controls_cfg.get('BACK_KEY', 'x'),
        move_slot=battle_cfg.get('MOVE_SLOT', 1),
        auto_catch=battle_cfg.get('AUTO_CATCH', False),
    )

    ai_agent = AIAgent(
        model=ai_cfg.get('MODEL', 'claude-haiku-4-5-20251001'),
        check_interval=ai_cfg.get('CHECK_INTERVAL', 10),
    )

    agent = AIAutonomousAgent(action, ai_agent, battle_handler)

    print('[BOT] Modo agente IA autonomo')
    print(f'[BOT] Modelo: {ai_agent.model}')
    print('[BOT] Pulsa Ctrl+C para parar')

    try:
        agent.run()
    except KeyboardInterrupt:
        agent.stop()
        print(f'\n[STATS] IA: {ai_agent.call_count} llamadas API')


if __name__ == "__main__":
    bot_cfg = getattr(config, 'bot', {})
    mode = bot_cfg.get('MODE', 'script')

    if mode == 'agent':
        run_agent_mode()
    else:
        run_script_mode()
