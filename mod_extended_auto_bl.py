# coding=utf-8
import BigWorld, game
import Keys
import functools
from gui import SystemMessages
from gui.battle_control.avatar_getter import getArena
from avatar_helpers import getAvatarDatabaseID
from adisp import async, process
from gui.battle_control.controllers import anonymizer_fakes_ctrl
from gui.battle_control.controllers import repositories
from gui.battle_control.controllers import feedback_events
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import BattleReplay
from messenger.m_constants import UserEntityScope
import logging
from messenger import MessengerEntry
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from Avatar import PlayerAvatar
from debug_utils import LOG_CURRENT_EXCEPTION
import inspect
from functools import wraps
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
import sys

_logger = logging.getLogger(__name__)
gui = MessengerEntry.g_instance.gui
DAMAGE_EVENTS = frozenset([BATTLE_EVENT_TYPE.RADIO_ASSIST,
 BATTLE_EVENT_TYPE.TRACK_ASSIST,
 BATTLE_EVENT_TYPE.STUN_ASSIST,
 BATTLE_EVENT_TYPE.DAMAGE,
 BATTLE_EVENT_TYPE.TANKING,
 BATTLE_EVENT_TYPE.RECEIVED_DAMAGE])
class SHELL_TYPES(object):
    HOLLOW_CHARGE = 'HOLLOW_CHARGE'
    HIGH_EXPLOSIVE = 'HIGH_EXPLOSIVE'
    ARMOR_PIERCING = 'ARMOR_PIERCING'
    ARMOR_PIERCING_HE = 'ARMOR_PIERCING_HE'
    ARMOR_PIERCING_CR = 'ARMOR_PIERCING_CR'
    SMOKE = 'SMOKE'

mod_toggle = {'aus': 0, 'only arty': 1, 'only HE': 2, 'HE + teamBL': 3}
_mod_toggle = mod_toggle['HE + teamBL']  # [0,1,2,3] für [aus, only arty, only HE, HE + teamBL]
# mit Config Datei können Zustände bleiben und sind nicht bei jedem Spielstart wieder auf Default

check_running = False

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

@process
@run_before(PlayerAvatar, 'onBattleEvents')
def before(events):
    global check_running
    global mod_toggle
    global _mod_toggle
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
        player = BigWorld.player()
        guiSessionProvider = player.guiSessionProvider
        id_list = []
        sessionProvider = dependency.instance(IBattleSessionProvider)
        setup = repositories.BattleSessionSetup(avatar=BigWorld.player(), sessionProvider=sessionProvider)
        adding2 = anonymizer_fakes_ctrl.AnonymizerFakesController(setup)
        if guiSessionProvider.shared.vehicleState.getControllingVehicleID() == player.playerVehicleID:
            for data in events:
                feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
                eventType = feedbackEvent.getBattleEventType()
                target_id = feedbackEvent.getTargetID()
                if eventType in DAMAGE_EVENTS:
                    extra = feedbackEvent.getExtra()
                    if extra:
                        if eventType == BATTLE_EVENT_TYPE.RECEIVED_DAMAGE:
                            if _mod_toggle == mod_toggle['HE + teamBL'] or _mod_toggle == mod_toggle['only HE']:
                                if extra.getShellType() == SHELL_TYPES.HIGH_EXPLOSIVE:
                                    id_list.append(str(target_id))
                            elif _mod_toggle == mod_toggle['only arty']:
                                tag_ = arena.vehicles[target_id]['vehicleType'].type.tags
                                if VEHICLE_CLASS_NAME.SPG in tag_:
                                    id_list.append(str(target_id))
        while len(id_list) > 0:
            check_running = True
            user = adding2.usersStorage.getUser(id_list[0], scope=UserEntityScope.BATTLE)
            if user is not None:
                if not (user.isFriend() or user.isIgnored()):
                    adding2.addBattleIgnored(id_list[0])
                    id_list.pop(0)
                    yield wait(1.1)
                else:
                    id_list.pop(0)
            else:
                adding2.addBattleIgnored(id_list[0])
                id_list.pop(0)
                yield wait(1.1)
            check_running = False




@async
def wait(seconds, callback):
    BigWorld.callback(seconds, lambda: callback(None))

@process
def arty_key():
    global check_running
    prebID = 0
    check_running = True
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
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
            tag = vData['vehicleType'].type.tags
            user = adding.usersStorage.getUser(av_ses_id, scope=UserEntityScope.BATTLE)
            if user is not None:
                if databaseID != databID and VEHICLE_CLASS_NAME.SPG in tag and not (user.isFriend() or user.isIgnored()):
                    if prebID > 0 and prebID != _prebattleID:
                        adding.addBattleIgnored(av_ses_id)
                        yield wait(1.1)
                    elif prebID == 0:
                        adding.addBattleIgnored(av_ses_id)
                        yield wait(1.1)
            else:
                if databaseID != databID and VEHICLE_CLASS_NAME.SPG in tag:
                    if prebID > 0 and prebID != _prebattleID:
                        adding.addBattleIgnored(av_ses_id)
                        yield wait(1.1)
                    elif prebID == 0:
                        adding.addBattleIgnored(av_ses_id)
                        yield wait(1.1)
    check_running = False

@process
def teambl_key():
    global check_running
    prebID = 0
    check_running = True
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
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
    check_running = False


def sendMessage(message, types):
    if BigWorld.player():
        SystemMessages.pushMessage(message, types)
    else:
        BigWorld.callback(1, functools.partial(sendMessage, message, types))


def key_events_():
    global mod_toggle
    global _mod_toggle
    old_handler = game.handleKeyEvent

    def new_handler(event):
        global mod_toggle
        global check_running
        global _mod_toggle
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isDown and mods == 4 and key == Keys.KEY_O:
            _mod_toggle += 1
            if _mod_toggle > 3:
                _mod_toggle = 0
            if _mod_toggle == mod_toggle['aus']:
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('Mod disabled', True)
                elif BigWorld.player():
                    sendMessage("Mod disabled", SystemMessages.SM_TYPE.Warning)
            elif _mod_toggle == mod_toggle['only arty']:
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('Only Cancer', True)
                elif BigWorld.player():
                    sendMessage("Only Cancer", SystemMessages.SM_TYPE.Warning)
            elif _mod_toggle == mod_toggle['only HE']:
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('Only HE', True)
                elif BigWorld.player():
                    sendMessage("Only HE", SystemMessages.SM_TYPE.Warning)
            else:
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('HE + blacklist Teams', True)
                elif BigWorld.player():
                    sendMessage("HE + blacklist Teams", SystemMessages.SM_TYPE.Warning)
        if _mod_toggle == mod_toggle['only arty']:
            BigWorld.callback(0, functools.partial(before, events))
            if isDown and mods == 4 and key == Keys.KEY_B:
                if check_running == False:
                    arty_key()
        elif _mod_toggle == mod_toggle['only HE']:
            BigWorld.callback(0, functools.partial(before, events))
        elif _mod_toggle == mod_toggle['HE + teamBL']:
            BigWorld.callback(0, functools.partial(before, events))
            if isDown and mods == 4 and key == Keys.KEY_B:
                if check_running == False:
                    teambl_key()
        old_handler(event)
        return

    game.handleKeyEvent = new_handler
    return


if not BattleReplay.isPlaying():
    key_events_()
