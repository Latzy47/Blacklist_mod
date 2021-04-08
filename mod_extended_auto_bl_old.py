# coding=utf-8
import datetime
import BigWorld

import BattleReplay
import Keys
import game
from Avatar import PlayerAvatar
from avatar_helpers import getAvatarDatabaseID
from gui.battle_control.avatar_getter import getArena
from gui.battle_control.controllers import anonymizer_fakes_ctrl
from gui.battle_control.controllers import feedback_events
from gui.battle_control.controllers import repositories
from helpers import dependency
from messenger.m_constants import UserEntityScope
from messenger.proto.xmpp.xmpp_constants import CONTACT_LIMIT
from messenger.proto.xmpp.contacts import ContactsManager
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from messenger.proto.xmpp.find_criteria import ItemsFindCriteria
from skeletons.gui.battle_session import IBattleSessionProvider
from extended_auto_bl_core import *

__author__ = 'FvckingLatzyMan'
__credits__ = ['lgfrbcsgo']
__version__ = '1.31'
__status__ = 'Production'

if not os.path.exists('res_mods/configs'):
    os.makedirs('res_mods/configs')


disabled_mode_dict, arty_mode_dict, he_mode_dict, he_bl_mode_dict = global_vars.loadModes()
disabled_mode = SchematicForMode(**disabled_mode_dict)
disabled_mode.removeNone()
arty_mode = SchematicForMode(**arty_mode_dict)
arty_mode.removeNone()
he_mode = SchematicForMode(**he_mode_dict)
he_mode.removeNone()
he_bl_mode = SchematicForMode(**he_bl_mode_dict)
he_bl_mode.removeNone()
global_vars.all_modes.append(disabled_mode)
global_vars.all_modes.append(arty_mode)
global_vars.all_modes.append(he_mode)
global_vars.all_modes.append(he_bl_mode)
global_vars.loadJson()


@process
def AUTO_add():
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


@run_before(PlayerAvatar, 'onBattleEvents')
def before(_, events):
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
        if arena.bonusType in global_vars.active_mode.auto_mode:
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
                                tag_ = arena.vehicles[target_id]['vehicleType'].type.tags
                                veh_name_ = arena.vehicles[target_id]['vehicleType'].type.name
                                if extra.getShellType() in global_vars.active_mode.shell_list or global_vars.active_mode.tank_cls & tag_ or veh_name_ in global_vars.active_mode.tanklist:  # isShellGold()
                                    if target_id != BigWorld.player().playerVehicleID:
                                        global_vars.id_list.append(str(target_id))
                                BigWorld.callback(0, AUTO_add)


@process
def pressed_key():
    prebID = 0
    global_vars.check_running = True
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
        if arena.bonusType in global_vars.active_mode.key_mode:
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
                tag = vData['vehicleType'].type.tags  # frozenset
                veh_name = vData['vehicleType'].type.name  # str
                user = adding.usersStorage.getUser(av_ses_id, scope=UserEntityScope.BATTLE)
                if user is not None:
                    if global_vars.active_mode.tank_cls_key or (global_vars.active_mode.tanklist[0] is not None):
                        if databaseID != databID and ((global_vars.active_mode.tank_cls_key & tag) or (veh_name in global_vars.active_mode.tanklist)):
                            if not (user.isFriend() or user.isIgnored()):
                                if prebID > 0 and prebID != _prebattleID:
                                    adding.addBattleIgnored(av_ses_id)
                                    yield wait(1.1)
                                elif prebID == 0:
                                    adding.addBattleIgnored(av_ses_id)
                                    yield wait(1.1)
                    else:
                        if databaseID != databID and not (user.isFriend() or user.isIgnored()):
                            if prebID > 0 and prebID != _prebattleID:
                                adding.addBattleIgnored(av_ses_id)
                                yield wait(1.1)
                            elif prebID == 0:
                                adding.addBattleIgnored(av_ses_id)
                                yield wait(1.1)
                else:
                    if global_vars.active_mode.tank_cls_key or (global_vars.active_mode.tanklist[0] is not None):
                        if databaseID != databID and ((global_vars.active_mode.tank_cls_key & tag) or (veh_name in global_vars.active_mode.tanklist)):
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
            SendGuiMessage('Blacklisting finished!')
    global_vars.check_running = False


@process
def clear_blacklist():
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is None and not global_vars.check_running:
        global_vars.check_running = True
        blacklisted_contacts = ContactsManager()
        all_users = blacklisted_contacts.usersStorage.getList(ItemsFindCriteria(XMPP_ITEM_TYPE.PERSISTENT_BLOCKING_LIST))
        idx = 0
        while idx < len(all_users) and global_vars.enable_clear:
            blacklisted_contacts.removeIgnored(all_users[idx].getID(), False)
            idx += 1
            yield wait(1.1)
            if idx % 500 == 0:
                users_left = len(all_users) - idx
                SendGuiMessage('There is '+str(datetime.timedelta(seconds=round(users_left*1.1)))+' left!')
        if idx == len(all_users)-1:
            SendGuiMessage('Cleared your blacklist!')
        global_vars.check_running = False


@run_before(game, 'handleKeyEvent')
def new_handler(event):
    if not BattleReplay.isPlaying():
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isDown and mods == 4 and key == Keys.KEY_O:
            global_vars.increment_mode()
            SendGuiMessage(global_vars.active_mode.name)
        elif isDown and mods == 4 and key == Keys.KEY_B:
            if not global_vars.check_running:
                pressed_key()
        elif isDown and mods == 2 and key == Keys.KEY_O:
            global_vars.toggle_extended()
            if not global_vars.extended:
                SendGuiMessage("Disabled extention")
            elif global_vars.extended:
                SendGuiMessage("Enabled extention")
        elif isDown and mods == 4 and key == Keys.KEY_C:
            global_vars.toggle_enable_clear()
            if not global_vars.enable_clear:
                SendGuiMessage("Disabled clearing your blacklist!")
            elif global_vars.enable_clear:
                contactsForTime = ContactsManager()
                all_bl_users = contactsForTime.usersStorage.getList(ItemsFindCriteria(XMPP_ITEM_TYPE.PERSISTENT_BLOCKING_LIST))
                SendGuiMessage("Enabled clearing your blacklist!\nMake sure you are in the garage!\nClearing everything will take {}!".format(str(datetime.timedelta(seconds=round(len(all_bl_users)*1.1)))))
        elif isDown and mods == 4 and key == Keys.KEY_X:
            if global_vars.enable_clear:
                clear_blacklist()


@run_before(PlayerAvatar, '_PlayerAvatar__onArenaPeriodChange')
def autoKeyPressed(_, period, __, ___, ____):
    if period == ARENA_PERIOD.BATTLE and global_vars.active_mode.auto_key_pressed:
        pressed_key()


if global_vars.extended:
    CONTACT_LIMIT.ROSTER_MAX_COUNT = global_vars.friends
    CONTACT_LIMIT.BLOCK_MAX_COUNT = global_vars.ignored
