# coding=utf-8

import BigWorld

import BattleReplay
from adisp import async, process
from avatar_helpers import getAvatarDatabaseID
from gui.battle_control.avatar_getter import getArena
from gui.battle_control.controllers import anonymizer_fakes_ctrl
from gui.battle_control.controllers import repositories
from helpers import dependency
from messenger.m_constants import UserEntityScope
from skeletons.gui.battle_session import IBattleSessionProvider
import logging
from functools import wraps
import inspect
import sys
from debug_utils import LOG_CURRENT_EXCEPTION
from Avatar import PlayerAvatar
_logger = logging.getLogger(__name__)


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


@process
def teambl_key():
    prebID = 0
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None and not BattleReplay.isPlaying():
        if arena.bonusType == 1:
            sessionProvider = dependency.instance(IBattleSessionProvider)
            setup = repositories.BattleSessionSetup(avatar=BigWorld.player(), sessionProvider=sessionProvider)
            adding = anonymizer_fakes_ctrl.AnonymizerFakesController(setup)
            databID = getAvatarDatabaseID()

            vehID = getattr(BigWorld.player(), 'playerVehicleID', None)
            if vehID is not None and vehID in arena.vehicles:
                prebID = arena.vehicles[vehID]['prebattleID']

            for (vehicleID, vData) in getArena().vehicles.iteritems():
                databaseID = vData['accountDBID']
                av_ses_id = vData['avatarSessionID']
                _prebattleID = vData['prebattleID']
                user = adding.usersStorage.getUser(av_ses_id, scope=UserEntityScope.BATTLE)
                if user is not None:
                    if databaseID != databID and not (user.isFriend() or user.isIgnored()):
                        if prebID > 0 and prebID != _prebattleID:
                            adding.addBattleIgnored(av_ses_id)
                            yield wait(1.1)
                        elif prebID == 0:
                            adding.addBattleIgnored(av_ses_id)
                            yield wait(1.1)
                else:
                    if databaseID != databID:
                        if prebID > 0 and prebID != _prebattleID:
                            adding.addBattleIgnored(av_ses_id)
                            yield wait(1.1)
                        elif prebID == 0:
                            adding.addBattleIgnored(av_ses_id)
                            yield wait(1.1)


@run_before(PlayerAvatar, '_PlayerAvatar__onArenaPeriodChange')
def test(_, period, __, ___, ____):
    if period == 3:
        teambl_key()
