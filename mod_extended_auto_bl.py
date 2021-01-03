# coding=utf-8
import functools
import logging
import sys
from functools import wraps

import BigWorld

import BattleReplay
import Keys
import game
import inspect
from Avatar import PlayerAvatar
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from adisp import async, process
from avatar_helpers import getAvatarDatabaseID
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.battle_control.avatar_getter import getArena
from gui.battle_control.controllers import anonymizer_fakes_ctrl
from gui.battle_control.controllers import feedback_events
from gui.battle_control.controllers import repositories
from helpers import dependency
from messenger import MessengerEntry
from messenger.m_constants import UserEntityScope
from messenger.proto.xmpp.xmpp_constants import CONTACT_LIMIT
from messenger.proto.xmpp.contacts import ContactsManager
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from messenger.proto.xmpp.find_criteria import ItemsFindCriteria
from skeletons.gui.battle_session import IBattleSessionProvider
from cls_file import *

if not os.path.exists('res_mods/configs'):
    os.makedirs('res_mods/configs')


_logger = logging.getLogger(__name__)  # _logger.error(msg)
gui = MessengerEntry.g_instance.gui
DAMAGE_EVENTS = frozenset([BATTLE_EVENT_TYPE.RADIO_ASSIST, BATTLE_EVENT_TYPE.TRACK_ASSIST,
                           BATTLE_EVENT_TYPE.STUN_ASSIST, BATTLE_EVENT_TYPE.DAMAGE,
                           BATTLE_EVENT_TYPE.TANKING, BATTLE_EVENT_TYPE.RECEIVED_DAMAGE])


global_vars.all_modes.append(disabled_mode)
global_vars.all_modes.append(arty_mode)
global_vars.all_modes.append(he_mode)
global_vars.all_modes.append(he_bl_mode)
global_vars.loadJson()


@process
def HE_add():
    if not global_vars.check_running:
        global_vars.check_running = True
        sessionProvider = dependency.instance(IBattleSessionProvider)
        setup = repositories.BattleSessionSetup(avatar=BigWorld.player(), sessionProvider=sessionProvider)
        adding2 = anonymizer_fakes_ctrl.AnonymizerFakesController(setup)
        while len(global_vars.id_list) > 0:
            user = adding2.usersStorage.getUser(global_vars.id_list[0], scope=UserEntityScope.BATTLE)
            if user is not None:
                if not (user.isFriend() or user.isIgnored()):
                    adding2.addBattleIgnored(global_vars.id_list[0])
                    yield wait(1.1)
                    global_vars.id_list.pop(0)
                else:
                    global_vars.id_list.pop(0)
            else:
                adding2.addBattleIgnored(global_vars.id_list[0])
                yield wait(1.1)
                global_vars.id_list.pop(0)
        global_vars.check_running = False


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


@run_before(PlayerAvatar, 'onBattleEvents')
def before(_, events):
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
        player = BigWorld.player()
        guiSessionProvider = player.guiSessionProvider
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
                                if extra.getShellType() == SHELL_TYPES.HIGH_EXPLOSIVE:  # isShellGold()
                                    if target_id != BigWorld.player().playerVehicleID:
                                        id_list.append(str(target_id))
                            elif _mod_toggle == mod_toggle['only arty']:
                                tag_ = arena.vehicles[target_id]['vehicleType'].type.tags
                                if VEHICLE_CLASS_NAME.SPG in tag_:
                                    if target_id != BigWorld.player().playerVehicleID:
                                        id_list.append(str(target_id))
                            BigWorld.callback(0, HE_add)


@async
def wait(seconds, callback):
    BigWorld.callback(seconds, lambda: callback(None))


@process
def pressed_key():
    prebID = 0
    global_vars.check_running = True
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
                if databaseID != databID and global_vars.active_mode.tank_cls_key in tag:
                    if not (user.isFriend() or user.isIgnored()):
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
        gui.addClientMessage('Blacklisted all artys', True)
    global_vars.check_running = False


@process
def teambl_key():
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
        gui.addClientMessage('Blacklisted all players', True)
    check_running = False


@process
def clear_blacklist():
    # TODO: handle lobby
    # TODO: vor dem Aufruf Zeitangabe
    blacklisted_contacts = ContactsManager()
    all_users = blacklisted_contacts.usersStorage.getList(ItemsFindCriteria(XMPP_ITEM_TYPE.PERSISTENT_BLOCKING_LIST))
    for idx, contact in enumerate(all_users, start=1):
        blacklisted_contacts.removeIgnored(contact.getID(), False)
        yield wait(1.1)
        if idx % 500 == 0:
            users_left = len(all_users) - idx
            # TODO: handle timestamp


def sendMessage(message, types=SystemMessages.SM_TYPE.Warning):
    if BigWorld.player():
        SystemMessages.pushMessage(message, types)
    else:
        BigWorld.callback(1, functools.partial(sendMessage, message, types))


def SendGuiMessage(message, types=SystemMessages.SM_TYPE.Warning):
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
        gui.addClientMessage(message, isCurrentPlayer=True)
    elif BigWorld.player():
        sendMessage(message, types=types)


@run_before(game, 'handleKeyEvent')
def new_handler(event):
    if not BattleReplay.isPlaying():
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isDown and mods == 4 and key == Keys.KEY_O:
            global_vars.increment_mode()
            SendGuiMessage(global_vars.active_mode.name)  # maybe handle empty list
        if isDown and mods == 4 and key == Keys.KEY_B:
            if not global_vars.check_running:
                pressed_key()
        if isDown and mods == 2 and key == Keys.KEY_O:
            global_vars.toggle_extended()
            if not global_vars.extended:
                SendGuiMessage("Disabled extention")
            elif global_vars.extended:
                SendGuiMessage("Enabled extention")


if global_vars.extended:
    CONTACT_LIMIT.ROSTER_MAX_COUNT = global_vars.friends
    CONTACT_LIMIT.BLOCK_MAX_COUNT = global_vars.ignored

