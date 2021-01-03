# coding=utf-8
import functools
import json
import logging
import sys
from functools import wraps

import BigWorld

import BattleReplay
import Keys
import game
import inspect
import os
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
DAMAGE_EVENTS = frozenset([BATTLE_EVENT_TYPE.RADIO_ASSIST,
 BATTLE_EVENT_TYPE.TRACK_ASSIST,
 BATTLE_EVENT_TYPE.STUN_ASSIST,
 BATTLE_EVENT_TYPE.DAMAGE,
 BATTLE_EVENT_TYPE.TANKING,
 BATTLE_EVENT_TYPE.RECEIVED_DAMAGE])


mod_toggle = {'aus': 0, 'only arty': 1, 'only HE': 2, 'HE + teamBL': 3}
check_running = False
config_data = {'mode': mod_toggle['HE + teamBL'], 'ignored': 1000000, 'friends': 1000000, 'extended': False}
id_list = []


def write_json():
    global config_data
    try:
        with open('res_mods/configs/extended_auto_bl.json', 'w') as f1:
            json.dump(config_data, f1, indent=2)
    except (IOError, ValueError):
        pass


if os.path.exists('res_mods/configs/extended_auto_bl.json'):
    with open('res_mods/configs/extended_auto_bl.json') as f:
        config_data = json.load(f)
else:
    write_json()

_mod_toggle = config_data['mode']
extended = config_data['extended']


@process
def HE_add():
    global id_list
    global check_running
    if not check_running:
        check_running = True
        sessionProvider = dependency.instance(IBattleSessionProvider)
        setup = repositories.BattleSessionSetup(avatar=BigWorld.player(), sessionProvider=sessionProvider)
        adding2 = anonymizer_fakes_ctrl.AnonymizerFakesController(setup)
        while len(id_list) > 0:
            user = adding2.usersStorage.getUser(id_list[0], scope=UserEntityScope.BATTLE)
            if user is not None:
                if not (user.isFriend() or user.isIgnored()):
                    adding2.addBattleIgnored(id_list[0])
                    yield wait(1.1)
                    id_list.pop(0)
                else:
                    id_list.pop(0)
            else:
                adding2.addBattleIgnored(id_list[0])
                yield wait(1.1)
                id_list.pop(0)
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


@run_before(PlayerAvatar, 'onBattleEvents')
def before(_, events):
    global mod_toggle
    global _mod_toggle
    global check_running
    global id_list
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
                if databaseID != databID and VEHICLE_CLASS_NAME.SPG in tag:
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
        global config_data
        global mod_toggle
        global check_running
        global _mod_toggle
        global extended
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isDown and mods == 4 and key == Keys.KEY_O:
            _mod_toggle += 1
            if _mod_toggle > 3:
                _mod_toggle = 0
            if _mod_toggle == mod_toggle['aus']:
                config_data['mode'] = mod_toggle['aus']
                write_json()
                SendGuiMessage("Mod disabled")
            elif _mod_toggle == mod_toggle['only arty']:
                config_data['mode'] = mod_toggle['only arty']
                write_json()
                SendGuiMessage("Only Arty")
            elif _mod_toggle == mod_toggle['only HE']:
                config_data['mode'] = mod_toggle['only HE']
                write_json()
                SendGuiMessage("Only HE")
            else:
                config_data['mode'] = mod_toggle['HE + teamBL']
                write_json()
                SendGuiMessage("HE + blacklist Teams")
        if _mod_toggle == mod_toggle['only arty']:
            if isDown and mods == 4 and key == Keys.KEY_B:
                if not check_running:
                    arty_key()
        elif _mod_toggle == mod_toggle['HE + teamBL']:
            if isDown and mods == 4 and key == Keys.KEY_B:
                if not check_running:
                    teambl_key()
        if isDown and mods == 2 and key == Keys.KEY_O:
            if not extended:
                extended = True
            elif extended:
                extended = False
            if not extended:
                config_data['extended'] = False
                write_json()
                SendGuiMessage("Disabled extention")
            elif extended:
                config_data['extended'] = True
                write_json()
                SendGuiMessage("Enabled extention")


if extended:
    CONTACT_LIMIT.ROSTER_MAX_COUNT = config_data['friends']
    CONTACT_LIMIT.BLOCK_MAX_COUNT = config_data['ignored']

