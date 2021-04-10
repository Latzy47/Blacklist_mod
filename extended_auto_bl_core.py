from constants import ARENA_BONUS_TYPE, ARENA_PERIOD
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
import json
import os
from debug_utils import LOG_CURRENT_EXCEPTION
import sys
import inspect
from functools import wraps
from adisp import async, process
from gui import SystemMessages
import functools
from messenger import MessengerEntry
import logging
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
import BigWorld

DAMAGE_EVENTS = frozenset([BATTLE_EVENT_TYPE.RADIO_ASSIST, BATTLE_EVENT_TYPE.TRACK_ASSIST,
                           BATTLE_EVENT_TYPE.STUN_ASSIST, BATTLE_EVENT_TYPE.DAMAGE,
                           BATTLE_EVENT_TYPE.TANKING, BATTLE_EVENT_TYPE.RECEIVED_DAMAGE])


class SHELL_TYPES(object):
    HOLLOW_CHARGE = 'HOLLOW_CHARGE'
    HIGH_EXPLOSIVE = 'HIGH_EXPLOSIVE'
    ARMOR_PIERCING = 'ARMOR_PIERCING'
    ARMOR_PIERCING_HE = 'ARMOR_PIERCING_HE'
    ARMOR_PIERCING_CR = 'ARMOR_PIERCING_CR'
    SMOKE = 'SMOKE'


class SchematicForMode(object):
    other_game_modes = (0, 2, 4, 5, 6, 7, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25,
                        26, 27, 28, 29, 30, 31, 32, 33)

    def __init__(self, shell_AP=False, shell_APCR=False, shell_HEAT=False,
                 shell_HE=False, random=False, random_key=False,
                 ranked=False, ranked_key=False,
                 other_modes=False, other_modes_key=False, light=False, light_key=False,
                 med=False, med_key=False, heavy=False, heavy_key=False, td=False, td_key=False, spg=False,
                 spg_key=False, tanklist=None, auto_key_pressed=False, wheeled=False, wheeled_key=False):
        self.shell_AP = None if not shell_AP else SHELL_TYPES.ARMOR_PIERCING
        self.shell_APCR = None if not shell_APCR else SHELL_TYPES.ARMOR_PIERCING_CR
        self.shell_HEAT = None if not shell_HEAT else SHELL_TYPES.HOLLOW_CHARGE
        self.shell_HE = None if not shell_HE else SHELL_TYPES.HIGH_EXPLOSIVE
        self.random = None if not random else ARENA_BONUS_TYPE.REGULAR
        self.random_key = None if not random_key else ARENA_BONUS_TYPE.REGULAR
        self.ranked = (None,) if not ranked else (ARENA_BONUS_TYPE.RANKED,)
        self.ranked_key = (None,) if not ranked_key else (ARENA_BONUS_TYPE.RANKED,)
        self.other_modes = (None,) if not other_modes else SchematicForMode.other_game_modes
        self.other_modes_key = (None,) if not other_modes_key else SchematicForMode.other_game_modes
        self.light = None if not light else VEHICLE_CLASS_NAME.LIGHT_TANK
        self.light_key = None if not light_key else VEHICLE_CLASS_NAME.LIGHT_TANK
        self.med = None if not med else VEHICLE_CLASS_NAME.MEDIUM_TANK
        self.med_key = None if not med_key else VEHICLE_CLASS_NAME.MEDIUM_TANK
        self.heavy = None if not heavy else VEHICLE_CLASS_NAME.HEAVY_TANK
        self.heavy_key = None if not heavy_key else VEHICLE_CLASS_NAME.HEAVY_TANK
        self.td = None if not td else VEHICLE_CLASS_NAME.AT_SPG
        self.td_key = None if not td_key else VEHICLE_CLASS_NAME.AT_SPG
        self.spg = None if not spg else VEHICLE_CLASS_NAME.SPG
        self.spg_key = None if not spg_key else VEHICLE_CLASS_NAME.SPG
        if tanklist is None:
            tanklist = [None]
        self.tanklist = tanklist
        self.auto_key_pressed = auto_key_pressed
        self.wheeled = None if not wheeled else 'wheeledVehicle'
        self.wheeled_key = None if not wheeled_key else 'wheeledVehicle'
        self.finishInit()

    def finishInit(self):
        self.shell_list = {self.shell_AP, self.shell_APCR, self.shell_HEAT, self.shell_HE}
        self.auto_mode = {self.random}
        self.auto_mode.update(self.ranked)
        self.auto_mode.update(self.other_modes)
        self.key_mode = {self.random_key}
        self.key_mode.update(self.ranked_key)
        self.key_mode.update(self.other_modes_key)
        self.tank_cls = {self.light, self.med, self.heavy, self.td, self.spg, self.wheeled}
        self.tank_cls_key = {self.light_key, self.med_key, self.heavy_key, self.td_key, self.spg_key, self.wheeled_key}
        self.removeNone()

    def removeNone(self):
        self.shell_list.discard(None)
        self.auto_mode.discard(None)
        self.key_mode.discard(None)
        self.tank_cls.discard(None)
        self.tank_cls_key.discard(None)


def hook(hook_handler):
    def build_decorator(module, func_name):
        def decorator(func):
            orig_func = getattr(module, func_name)

            @wraps(orig_func)
            def func_wrapper(*args, **kwargs):
                return hook_handler(orig_func, func, *args, **kwargs)

            if inspect.ismodule(module):
                setattr(sys.modules[module.__name__], func_name, func_wrapper)
            elif inspect.isclass(module):
                setattr(module, func_name, func_wrapper)

            return func

        return decorator

    return build_decorator


def sendMessage(message, types=SystemMessages.SM_TYPE.Warning):
    if BigWorld.player():
        SystemMessages.pushMessage(message, types)
    else:
        BigWorld.callback(1, functools.partial(sendMessage, message, types))


def SendGuiMessage(message, types=SystemMessages.SM_TYPE.Warning, enable=True):
    if enable:
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            gui.addClientMessage(message, isCurrentPlayer=True)
        elif BigWorld.player():
            sendMessage(message, types=types)


@hook
def run_before(orig_func, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except:
        LOG_CURRENT_EXCEPTION()
    finally:
        return orig_func(*args, **kwargs)


@async
def wait(seconds, callback):
    BigWorld.callback(seconds, lambda: callback(None))


_logger = logging.getLogger(__name__)  # _logger.error(msg)
gui = MessengerEntry.g_instance.gui
