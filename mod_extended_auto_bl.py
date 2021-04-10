# -*- coding: utf-8 -*-
from PYmodsCore import PYmodsConfigInterface, checkKeys
from PYmodsCore.delayed.support import ConfigInterface as CI
from PYmodsCore.config.interfaces.PyMods import PYmodsSettingContainer
from gui.modsListApi import g_modsListApi
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
__date__ = '09.04.2021'
__credits__ = ['lgfrbcsgo', 'Polyacov_Yury', 'Iliev Renat', 'Andruschyshyn Andrey']
__version__ = '2.0'
__status__ = 'Production'


class ConfigInterface(PYmodsConfigInterface):
    def __init__(self):
        super(ConfigInterface, self).__init__()
        self.enable_clear = False
        self.id_list = []
        self.check_running = False

    def init(self):
        self.ID = 'X_Auto_BL'
        self.version = '%s (%s)' % (__version__, __date__)
        self.defaultKeys = {'hotkey1': [Keys.KEY_O, [Keys.KEY_LALT, Keys.KEY_RALT]],  # switch modes
                            'hotkey2': [Keys.KEY_B, [Keys.KEY_LALT, Keys.KEY_RALT]],  # key function
                            'hotkey3': [Keys.KEY_C, [Keys.KEY_LALT, Keys.KEY_RALT]],  # enable clear
                            'hotkey4': [Keys.KEY_X, [Keys.KEY_LALT, Keys.KEY_RALT]]}  # start clear
        self.data = {'enabled': True,
                     'ignored': 1000000,
                     'extended': False,
                     'friends': 1000000,
                     'hotkey1': self.defaultKeys['hotkey1'],
                     'hotkey2': self.defaultKeys['hotkey2'],
                     'hotkey3': self.defaultKeys['hotkey3'],
                     'hotkey4': self.defaultKeys['hotkey4']}
        self.i18n = {
            'UI_description': 'Extended automated blacklist',
            'UI_setting_ignored_text': 'Number blacklist',
            'UI_setting_ignored_tooltip': 'This number shows the length of your blacklist.\n'
                                          'Restarting the game is required to take effect.',
            'UI_setting_extended_text': 'Extend lists',
            'UI_setting_extended_tooltip': 'This enables/disables the extention of the blacklist'
                                           ' and friendlist.\n'
                                           'Restarting the game is required to take effect.',
            'UI_setting_friends_text': 'Number friendlist',
            'UI_setting_friends_tooltip': 'This number shows the length of your friendlist.\n'
                                          'Restarting the game is required to take effect.',
            'UI_setting_hotkey1_text': 'Switch modes',
            'UI_setting_hotkey1_tooltip': 'Pressing this hotkey will switch between modes.',
            'UI_setting_hotkey2_text': 'Blacklist key',
            'UI_setting_hotkey2_tooltip': 'Pressing this hotkey will blacklist your desired tanks.',
            'UI_setting_hotkey3_text': 'Clear enable',
            'UI_setting_hotkey3_tooltip': 'Pressing this hotkey will enable/disable clearing your blacklist.',
            'UI_setting_hotkey4_text': 'Clear start',
            'UI_setting_hotkey4_tooltip': 'Pressing this hotkey will start clearing your blacklist.'}
        super(ConfigInterface, self).init()
        self.containerClass = MyPYmodsSettingContainer
        self.modSettingsID = 'x_auto_bl'
        self.modsGroup = 'xAutoBl'
        self.author = 'by %s' % __author__

    def createTemplate(self):
        return {'modDisplayName': self.i18n['UI_description'],
                'enabled': self.data['enabled'],
                'column1': [self.tb.createSlider('ignored', 5000, 1000000, 5000),
                            self.tb.createSlider('friends', 5000, 1000000, 5000),
                            self.tb.createHotKey('hotkey1')],
                'column2': [self.tb.createControl('extended'),
                            self.tb.createHotKey('hotkey2'),
                            self.tb.createHotKey('hotkey3'),
                            self.tb.createHotKey('hotkey4')]}

    def onMSADestroy(self):
        self.readCurrentSettings()

    def onHotkeyPressed(self, event):
        if not event.isKeyDown() or not self.data['enabled']:
            return
        if checkKeys(self.data['hotkey3']):
            self.toggle_enable_clear()
            if not self.enable_clear:
                SendGuiMessage("Disabled clearing your blacklist!")
            elif self.enable_clear:
                contactsForTime = ContactsManager()
                all_bl_users = contactsForTime.usersStorage.getList(
                    ItemsFindCriteria(XMPP_ITEM_TYPE.PERSISTENT_BLOCKING_LIST))
                SendGuiMessage(
                    "Enabled clearing your blacklist!\nMake sure you are in the garage!\nClearing everything will take {}!".format(
                        str(datetime.timedelta(seconds=round(len(all_bl_users) * 1.1)))))
        elif checkKeys(self.data['hotkey4']):
            if self.enable_clear:
                self.clear_blacklist()

    @process
    def clear_blacklist(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is None and not self.check_running:
            self.check_running = True
            blacklisted_contacts = ContactsManager()
            all_users = blacklisted_contacts.usersStorage.getList(
                ItemsFindCriteria(XMPP_ITEM_TYPE.PERSISTENT_BLOCKING_LIST))
            idx = 0
            while idx < len(all_users) and self.enable_clear:
                blacklisted_contacts.removeIgnored(all_users[idx].getID(), False)
                idx += 1
                yield wait(1.1)
                if idx % 500 == 0:
                    users_left = len(all_users) - idx
                    SendGuiMessage('There is ' + str(datetime.timedelta(seconds=round(users_left * 1.1))) + ' left!')
            if idx == len(all_users):
                SendGuiMessage('Cleared your blacklist!')
            self.check_running = False

    def toggle_enable_clear(self):
        if not self.enable_clear:
            self.enable_clear = True
        elif self.enable_clear:
            self.enable_clear = False


class ConfigInterface2(PYmodsConfigInterface):
    def __init__(self):
        super(ConfigInterface2, self).__init__()

    def init(self):
        self.ID = 'X_Auto_BL_2'
        self.version = '%s (%s)' % (__version__, __date__)
        self.data = {'enabled': True,
                     'name': 'Arty only',
                     'shell_AP': False,
                     'shell_APCR': False,
                     'shell_HEAT': False,
                     'shell_HE': False,
                     'random': True,
                     'random_key': True,
                     'ranked': True,
                     'ranked_key': True,
                     'other_modes': False,
                     'other_modes_key': False,
                     'light': False,
                     'light_key': False,
                     'med': False,
                     'med_key': False,
                     'heavy': False,
                     'heavy_key': False,
                     'td': False,
                     'td_key': False,
                     'spg': True,
                     'spg_key': True,
                     'tanklist': [None],
                     'auto_key_pressed': False,
                     'wheeled': False,
                     'wheeled_key': False,
                     'modeNumber': 0,
                     'currentNumber': 1,
                     'activeMode': False,
                     'specific_tank': 'Some specific tank'}
        self.i18n = {
            'UI_description': 'Mode 2',
            'UI_setting_name_text': 'Mode name',
            'UI_setting_name_tooltip': 'You can rename the mode to whatever you want.',
            'UI_setting_shell_AP_text': 'AP',
            'UI_setting_shell_AP_tooltip': 'Everyone who hits you with AP will be added to your blacklist.',
            'UI_setting_shell_APCR_text': 'APCR',
            'UI_setting_shell_APCR_tooltip': 'Everyone who hits you with APCR will be added to your blacklist.',
            'UI_setting_shell_HEAT_text': 'HEAT',
            'UI_setting_shell_HEAT_tooltip': 'Everyone who hits you with HEAT will be added to your blacklist.',
            'UI_setting_shell_HE_text': 'HE',
            'UI_setting_shell_HE_tooltip': 'Everyone who hits you with HE will be added to your blacklist.',
            'UI_setting_random_text': 'Random',
            'UI_setting_random_tooltip': 'Adding to your blacklist by shots will work in randoms.',
            'UI_setting_random_key_text': 'Random key',
            'UI_setting_random_key_tooltip': 'Adding to your blacklist by hotkey will work in randoms.',
            'UI_setting_ranked_text': 'Ranked',
            'UI_setting_ranked_tooltip': 'Adding to your blacklist by shots will work in ranked.',
            'UI_setting_ranked_key_text': 'Ranked key',
            'UI_setting_ranked_key_tooltip': 'Adding to your blacklist by hotkey will work in ranked.',
            'UI_setting_other_modes_text': 'Other modes',
            'UI_setting_other_modes_tooltip': 'Adding to your blacklist by shots will work in all modes '
                                              '(excluding random and ranked).',
            'UI_setting_other_modes_key_text': 'Other modes key',
            'UI_setting_other_modes_key_tooltip': 'Adding to your blacklist by hotkey will work in all modes '
                                                  '(excluding random and ranked).',
            'UI_setting_light_text': 'Light',
            'UI_setting_light_tooltip': 'Every light that hits you will be added to your blacklist.',
            'UI_setting_light_key_text': 'Light key',
            'UI_setting_light_key_tooltip': 'By pressing the blacklist key every light will be added to '
                                            'your blacklist.',
            'UI_setting_med_text': 'Medium',
            'UI_setting_med_tooltip': 'Every medium that hits you will be added to your blacklist.',
            'UI_setting_med_key_text': 'Medium key',
            'UI_setting_med_key_tooltip': 'By pressing the blacklist key every medium will be added to '
                                          'your blacklist.',
            'UI_setting_heavy_text': 'Heavy',
            'UI_setting_heavy_tooltip': 'Every heavy that hits you will be added to your blacklist.',
            'UI_setting_heavy_key_text': 'Heavy key',
            'UI_setting_heavy_key_tooltip': 'By pressing the blacklist key every heavy will be added to '
                                            'your blacklist.',
            'UI_setting_td_text': 'TD',
            'UI_setting_td_tooltip': 'Every TD that hits you will be added to your blacklist.',
            'UI_setting_td_key_text': 'TD key',
            'UI_setting_td_key_tooltip': 'By pressing the blacklist key every TD will be added to '
                                         'your blacklist.',
            'UI_setting_spg_text': 'Arty',
            'UI_setting_spg_tooltip': 'Every arty that hits you will be added to your blacklist.',
            'UI_setting_spg_key_text': 'Arty key',
            'UI_setting_spg_key_tooltip': 'By pressing the blacklist key every arty will be added to '
                                          'your blacklist.',
            'UI_setting_auto_key_pressed_text': 'Auto key pressed',
            'UI_setting_auto_key_pressed_tooltip': 'With the start of a battle the blacklist key will be '
                                                   'automatically triggered.',
            'UI_setting_wheeled_text': 'Wheeled',
            'UI_setting_wheeled_tooltip': 'Every wheeled vehicle that hits you will be added to your blacklist.',
            'UI_setting_wheeled_key_text': 'Wheeled key',
            'UI_setting_wheeled_key_tooltip': 'By pressing the blacklist key every wheeled vehicle will '
                                              'be added to your blacklist.',
            'UI_setting_specific_tank_text': 'Some specific tank',
            'UI_setting_specific_tank_tooltip': 'You can add here specific tanks to be blacklisted. Read the '
                                                'README-file for further information. You will need the button below.'
        }
        super(ConfigInterface2, self).init()
        self.containerClass = MyPYmodsSettingContainer
        self.modSettingsID = 'x_auto_bl'
        self.modsGroup = 'xAutoBl'
        self.author = 'by %s' % __author__

    def createTemplate(self):
        return {'modDisplayName': self.i18n['UI_description'],
                'enabled': self.data['enabled'],
                'column1': [self.tb.createControl('name', 'TextInput'),
                            self.tb.createControl('random'),
                            self.tb.createControl('ranked'),
                            self.tb.createControl('other_modes'),
                            self.tb.createControl('light'),
                            self.tb.createControl('med'),
                            self.tb.createControl('heavy'),
                            self.tb.createControl('td'),
                            self.tb.createControl('spg'),
                            self.tb.createControl('wheeled'),
                            self.tb.createControl('shell_AP'),
                            self.tb.createControl('shell_HEAT'),
                            self.tb.createControl('auto_key_pressed')],
                'column2': [self.tb.createControl('specific_tank', 'TextInput'),
                            self.tb.createControl('random_key', button={'iconSource': '../maps/icons/buttons/swap2.png'}),
                            self.tb.createControl('ranked_key'),
                            self.tb.createControl('other_modes_key'),
                            self.tb.createControl('light_key'),
                            self.tb.createControl('med_key'),
                            self.tb.createControl('heavy_key'),
                            self.tb.createControl('td_key'),
                            self.tb.createControl('spg_key'),
                            self.tb.createControl('wheeled_key'),
                            self.tb.createControl('shell_APCR'),
                            self.tb.createControl('shell_HE')]}

    def onHotkeyPressed(self, event):
        if not event.isKeyDown() or not self.data['enabled']:
            return
        if checkKeys(config0.getData()['hotkey1']):
            if self.data['currentNumber'] > 0:
                self.data['currentNumber'] = 0
            else:
                self.data['currentNumber'] += 1
            self.data['activeMode'] = self.data['currentNumber'] == self.data['modeNumber']
            self.writeDataJson()
            if self.data['activeMode']:
                SendGuiMessage(self.data['name'])
        elif self.data['activeMode'] and checkKeys(config0.getData()['hotkey2']):
            if not config0.check_running:
                self.pressed_key()

    def onApplySettings(self, settings):
        super(ConfigInterface2, self).onApplySettings(settings)
        if 'tanklist' in settings:
            self.schematic = SchematicForMode(shell_AP=settings['shell_AP'], shell_APCR=settings['shell_APCR'],
                                              shell_HEAT=settings['shell_HEAT'], shell_HE=settings['shell_HE'],
                                              random=settings['random'], random_key=settings['random_key'],
                                              ranked=settings['ranked'], ranked_key=settings['ranked_key'],
                                              other_modes=settings['other_modes'],
                                              other_modes_key=settings['other_modes_key'],
                                              light=settings['light'], light_key=settings['light_key'],
                                              med=settings['med'], med_key=settings['med_key'], heavy=settings['heavy'],
                                              heavy_key=settings['heavy_key'], td=settings['td'], td_key=settings['td_key'],
                                              spg=settings['spg'], spg_key=settings['spg_key'],
                                              tanklist=settings['tanklist'],
                                              auto_key_pressed=settings['auto_key_pressed'], wheeled=settings['wheeled'],
                                              wheeled_key=settings['wheeled_key'])
        else:
            self.schematic = SchematicForMode(shell_AP=settings['shell_AP'], shell_APCR=settings['shell_APCR'],
                                              shell_HEAT=settings['shell_HEAT'], shell_HE=settings['shell_HE'],
                                              random=settings['random'], random_key=settings['random_key'],
                                              ranked=settings['ranked'], ranked_key=settings['ranked_key'],
                                              other_modes=settings['other_modes'],
                                              other_modes_key=settings['other_modes_key'],
                                              light=settings['light'], light_key=settings['light_key'],
                                              med=settings['med'], med_key=settings['med_key'], heavy=settings['heavy'],
                                              heavy_key=settings['heavy_key'], td=settings['td'],
                                              td_key=settings['td_key'],
                                              spg=settings['spg'], spg_key=settings['spg_key'],
                                              tanklist=self.data['tanklist'],
                                              auto_key_pressed=settings['auto_key_pressed'],
                                              wheeled=settings['wheeled'],
                                              wheeled_key=settings['wheeled_key'])

    def onButtonPress(self, vName, value):
        if vName != 'random_key':
            return
        if self.data['specific_tank'] in self.data['tanklist']:
            self.data['tanklist'].remove(self.data['specific_tank'])
            SendGuiMessage('%s was removed.' % self.data['specific_tank'])
        else:
            self.data['tanklist'].append(self.data['specific_tank'])
            SendGuiMessage('%s was added.' % self.data['specific_tank'])
        self.onApplySettings(self.data)

    @process
    def pressed_key(self):  # not working in training room coz prebID identical
        prebID = 0
        config0.check_running = True
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            if arena.bonusType in self.schematic.key_mode:
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
                        if self.schematic.tank_cls_key or len(self.schematic.tanklist) > 1:
                            if databaseID != databID and ((self.schematic.tank_cls_key & tag) or (
                                    veh_name in self.schematic.tanklist)):
                                if not (user.isFriend() or user.isIgnored()):
                                    if prebID > 0 and prebID != _prebattleID:
                                        adding.addBattleIgnored(av_ses_id)
                                        yield wait(1.1)
                                    elif prebID == 0:
                                        adding.addBattleIgnored(av_ses_id)
                                        yield wait(1.1)
                    else:
                        if self.schematic.tank_cls_key or len(self.schematic.tanklist) > 1:
                            if databaseID != databID and ((self.schematic.tank_cls_key & tag) or (
                                    veh_name in self.schematic.tanklist)):
                                if prebID > 0 and prebID != _prebattleID:
                                    adding.addBattleIgnored(av_ses_id)
                                    yield wait(1.1)
                                elif prebID == 0:
                                    adding.addBattleIgnored(av_ses_id)
                                    yield wait(1.1)
                SendGuiMessage('Blacklisting finished!')
        config0.check_running = False


class ConfigInterface3(PYmodsConfigInterface):
    def __init__(self):
        super(ConfigInterface3, self).__init__()

    def init(self):
        self.ID = 'X_Auto_BL_3'
        self.version = '%s (%s)' % (__version__, __date__)
        self.data = {'enabled': True,
                     'name': 'HE + blacklist teams',
                     'shell_AP': False,
                     'shell_APCR': False,
                     'shell_HEAT': False,
                     'shell_HE': True,
                     'random': True,
                     'random_key': True,
                     'ranked': True,
                     'ranked_key': True,
                     'other_modes': False,
                     'other_modes_key': False,
                     'light': False,
                     'light_key': True,
                     'med': False,
                     'med_key': True,
                     'heavy': False,
                     'heavy_key': True,
                     'td': False,
                     'td_key': True,
                     'spg': False,
                     'spg_key': True,
                     'tanklist': [None],
                     'auto_key_pressed': False,
                     'wheeled': False,
                     'wheeled_key': False,
                     'modeNumber': 1,
                     'currentNumber': 1,
                     'activeMode': True,
                     'specific_tank': 'Some specific tank'}
        self.i18n = {
            'UI_description': 'Mode 1',
            'UI_setting_name_text': 'Mode name',
            'UI_setting_name_tooltip': 'You can rename the mode to whatever you want.',
            'UI_setting_shell_AP_text': 'AP',
            'UI_setting_shell_AP_tooltip': 'Everyone who hits you with AP will be added to your blacklist.',
            'UI_setting_shell_APCR_text': 'APCR',
            'UI_setting_shell_APCR_tooltip': 'Everyone who hits you with APCR will be added to your blacklist.',
            'UI_setting_shell_HEAT_text': 'HEAT',
            'UI_setting_shell_HEAT_tooltip': 'Everyone who hits you with HEAT will be added to your blacklist.',
            'UI_setting_shell_HE_text': 'HE',
            'UI_setting_shell_HE_tooltip': 'Everyone who hits you with HE will be added to your blacklist.',
            'UI_setting_random_text': 'Random',
            'UI_setting_random_tooltip': 'Adding to your blacklist by shots will work in randoms.',
            'UI_setting_random_key_text': 'Random key',
            'UI_setting_random_key_tooltip': 'Adding to your blacklist by hotkey will work in randoms.',
            'UI_setting_ranked_text': 'Ranked',
            'UI_setting_ranked_tooltip': 'Adding to your blacklist by shots will work in ranked.',
            'UI_setting_ranked_key_text': 'Ranked key',
            'UI_setting_ranked_key_tooltip': 'Adding to your blacklist by hotkey will work in ranked.',
            'UI_setting_other_modes_text': 'Other modes',
            'UI_setting_other_modes_tooltip': 'Adding to your blacklist by shots will work in all modes '
                                              '(excluding random and ranked).',
            'UI_setting_other_modes_key_text': 'Other modes key',
            'UI_setting_other_modes_key_tooltip': 'Adding to your blacklist by hotkey will work in all modes '
                                                  '(excluding random and ranked).',
            'UI_setting_light_text': 'Light',
            'UI_setting_light_tooltip': 'Every light that hits you will be added to your blacklist.',
            'UI_setting_light_key_text': 'Light key',
            'UI_setting_light_key_tooltip': 'By pressing the blacklist key every light will be added to '
                                            'your blacklist.',
            'UI_setting_med_text': 'Medium',
            'UI_setting_med_tooltip': 'Every medium that hits you will be added to your blacklist.',
            'UI_setting_med_key_text': 'Medium key',
            'UI_setting_med_key_tooltip': 'By pressing the blacklist key every medium will be added to '
                                          'your blacklist.',
            'UI_setting_heavy_text': 'Heavy',
            'UI_setting_heavy_tooltip': 'Every heavy that hits you will be added to your blacklist.',
            'UI_setting_heavy_key_text': 'Heavy key',
            'UI_setting_heavy_key_tooltip': 'By pressing the blacklist key every heavy will be added to '
                                            'your blacklist.',
            'UI_setting_td_text': 'TD',
            'UI_setting_td_tooltip': 'Every TD that hits you will be added to your blacklist.',
            'UI_setting_td_key_text': 'TD key',
            'UI_setting_td_key_tooltip': 'By pressing the blacklist key every TD will be added to '
                                         'your blacklist.',
            'UI_setting_spg_text': 'Arty',
            'UI_setting_spg_tooltip': 'Every arty that hits you will be added to your blacklist.',
            'UI_setting_spg_key_text': 'Arty key',
            'UI_setting_spg_key_tooltip': 'By pressing the blacklist key every arty will be added to '
                                          'your blacklist.',
            'UI_setting_auto_key_pressed_text': 'Auto key pressed',
            'UI_setting_auto_key_pressed_tooltip': 'With the start of a battle the blacklist key will be '
                                                   'automatically triggered.',
            'UI_setting_wheeled_text': 'Wheeled',
            'UI_setting_wheeled_tooltip': 'Every wheeled vehicle that hits you will be added to your blacklist.',
            'UI_setting_wheeled_key_text': 'Wheeled key',
            'UI_setting_wheeled_key_tooltip': 'By pressing the blacklist key every wheeled vehicle will '
                                              'be added to your blacklist.',
            'UI_setting_specific_tank_text': 'Some specific tank',
            'UI_setting_specific_tank_tooltip': 'You can add here specific tanks to be blacklisted. Read the '
                                                'README-file for further information. You will need the button below.'
        }
        super(ConfigInterface3, self).init()
        self.containerClass = MyPYmodsSettingContainer
        self.modSettingsID = 'x_auto_bl'
        self.modsGroup = 'xAutoBl'
        self.author = 'by %s' % __author__

    def createTemplate(self):
        return {'modDisplayName': self.i18n['UI_description'],
                'enabled': self.data['enabled'],
                'column1': [self.tb.createControl('name', 'TextInput'),
                            self.tb.createControl('random'),
                            self.tb.createControl('ranked'),
                            self.tb.createControl('other_modes'),
                            self.tb.createControl('light'),
                            self.tb.createControl('med'),
                            self.tb.createControl('heavy'),
                            self.tb.createControl('td'),
                            self.tb.createControl('spg'),
                            self.tb.createControl('wheeled'),
                            self.tb.createControl('shell_AP'),
                            self.tb.createControl('shell_HEAT'),
                            self.tb.createControl('auto_key_pressed')],
                'column2': [self.tb.createControl('specific_tank', 'TextInput'),
                            self.tb.createControl('random_key', button={'iconSource': '../maps/icons/buttons/swap2.png'}),
                            self.tb.createControl('ranked_key'),
                            self.tb.createControl('other_modes_key'),
                            self.tb.createControl('light_key'),
                            self.tb.createControl('med_key'),
                            self.tb.createControl('heavy_key'),
                            self.tb.createControl('td_key'),
                            self.tb.createControl('spg_key'),
                            self.tb.createControl('wheeled_key'),
                            self.tb.createControl('shell_APCR'),
                            self.tb.createControl('shell_HE')]}

    def onHotkeyPressed(self, event):
        if not event.isKeyDown() or not self.data['enabled']:
            return
        if checkKeys(config0.getData()['hotkey1']):
            if self.data['currentNumber'] > 0:
                self.data['currentNumber'] = 0
            else:
                self.data['currentNumber'] += 1
            self.data['activeMode'] = self.data['currentNumber'] == self.data['modeNumber']
            self.writeDataJson()
            if self.data['activeMode']:
                SendGuiMessage(self.data['name'])
        elif self.data['activeMode'] and checkKeys(config0.getData()['hotkey2']):
            if not config0.check_running:
                self.pressed_key()

    def onApplySettings(self, settings):
        super(ConfigInterface3, self).onApplySettings(settings)
        if 'tanklist' in settings:
            self.schematic = SchematicForMode(shell_AP=settings['shell_AP'], shell_APCR=settings['shell_APCR'],
                                              shell_HEAT=settings['shell_HEAT'], shell_HE=settings['shell_HE'],
                                              random=settings['random'], random_key=settings['random_key'],
                                              ranked=settings['ranked'], ranked_key=settings['ranked_key'],
                                              other_modes=settings['other_modes'],
                                              other_modes_key=settings['other_modes_key'],
                                              light=settings['light'], light_key=settings['light_key'],
                                              med=settings['med'], med_key=settings['med_key'], heavy=settings['heavy'],
                                              heavy_key=settings['heavy_key'], td=settings['td'], td_key=settings['td_key'],
                                              spg=settings['spg'], spg_key=settings['spg_key'],
                                              tanklist=settings['tanklist'],
                                              auto_key_pressed=settings['auto_key_pressed'], wheeled=settings['wheeled'],
                                              wheeled_key=settings['wheeled_key'])
        else:
            self.schematic = SchematicForMode(shell_AP=settings['shell_AP'], shell_APCR=settings['shell_APCR'],
                                              shell_HEAT=settings['shell_HEAT'], shell_HE=settings['shell_HE'],
                                              random=settings['random'], random_key=settings['random_key'],
                                              ranked=settings['ranked'], ranked_key=settings['ranked_key'],
                                              other_modes=settings['other_modes'],
                                              other_modes_key=settings['other_modes_key'],
                                              light=settings['light'], light_key=settings['light_key'],
                                              med=settings['med'], med_key=settings['med_key'], heavy=settings['heavy'],
                                              heavy_key=settings['heavy_key'], td=settings['td'],
                                              td_key=settings['td_key'],
                                              spg=settings['spg'], spg_key=settings['spg_key'],
                                              tanklist=self.data['tanklist'],
                                              auto_key_pressed=settings['auto_key_pressed'],
                                              wheeled=settings['wheeled'],
                                              wheeled_key=settings['wheeled_key'])

    def onButtonPress(self, vName, value):
        if vName != 'random_key':
            return
        if self.data['specific_tank'] in self.data['tanklist']:
            self.data['tanklist'].remove(self.data['specific_tank'])
            SendGuiMessage('%s was removed.' % self.data['specific_tank'])
        else:
            self.data['tanklist'].append(self.data['specific_tank'])
            SendGuiMessage('%s was added.' % self.data['specific_tank'])
        self.onApplySettings(self.data)

    @process
    def pressed_key(self):  # not working in training room coz prebID identical
        prebID = 0
        config0.check_running = True
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            if arena.bonusType in self.schematic.key_mode:
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
                        if self.schematic.tank_cls_key or len(self.schematic.tanklist) > 1:
                            if databaseID != databID and ((self.schematic.tank_cls_key & tag) or (
                                    veh_name in self.schematic.tanklist)):
                                if not (user.isFriend() or user.isIgnored()):
                                    if prebID > 0 and prebID != _prebattleID:
                                        adding.addBattleIgnored(av_ses_id)
                                        yield wait(1.1)
                                    elif prebID == 0:
                                        adding.addBattleIgnored(av_ses_id)
                                        yield wait(1.1)
                    else:
                        if self.schematic.tank_cls_key or len(self.schematic.tanklist) > 1:
                            if databaseID != databID and ((self.schematic.tank_cls_key & tag) or (
                                    veh_name in self.schematic.tanklist)):
                                if prebID > 0 and prebID != _prebattleID:
                                    adding.addBattleIgnored(av_ses_id)
                                    yield wait(1.1)
                                elif prebID == 0:
                                    adding.addBattleIgnored(av_ses_id)
                                    yield wait(1.1)
                SendGuiMessage('Blacklisting finished!')
        config0.check_running = False


class MyPYmodsSettingContainer(PYmodsSettingContainer):
    def init(self):
        super(MyPYmodsSettingContainer, self).init()
        self.i18n = {
            'modsListApiName': "Blacklist mod",
            'modsListApiDescription': "Extended automated blacklist modification settings",
            'windowTitle': "Blacklist mod settings",
            'enableButtonTooltip': '{HEADER}ON/OFF{/HEADER}{BODY}Enable/disable this mod{/BODY}'}


# disable his patreon
class NewCI(CI):
    def createTemplate(self):
        return {}


@process
def AUTO_add():
    if not config0.check_running:
        config0.check_running = True
        sessionProvider = dependency.instance(IBattleSessionProvider)
        setup = repositories.BattleSessionSetup(avatar=BigWorld.player(), sessionProvider=sessionProvider)
        adding2 = anonymizer_fakes_ctrl.AnonymizerFakesController(setup)
        while len(config0.id_list) > 0:
            user = adding2.usersStorage.getUser(config0.id_list[0], scope=UserEntityScope.BATTLE)
            if user is not None:
                if not (user.isFriend() or user.isIgnored()):
                    adding2.addBattleIgnored(config0.id_list[0])
                    yield wait(1.1)
            else:
                adding2.addBattleIgnored(config0.id_list[0])
                yield wait(1.1)
            config0.id_list.pop(0)
        config0.check_running = False


@run_before(PlayerAvatar, 'onBattleEvents')
def before(_, events):
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
        conf_1_data = config1.getData()
        if conf_1_data['enabled'] and conf_1_data['activeMode']:
            if arena.bonusType in config1.schematic.auto_mode:
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
                                    if extra.getShellType() in config1.schematic.shell_list or config1.schematic.tank_cls & tag_ or veh_name_ in config1.schematic.tanklist:  # isShellGold()
                                        if target_id != BigWorld.player().playerVehicleID:
                                            config0.id_list.append(str(target_id))
                                    BigWorld.callback(0, AUTO_add)
            return
        conf_2_data = config2.getData()
        if conf_2_data['enabled'] and conf_2_data['activeMode']:
            if arena.bonusType in config2.schematic.auto_mode:
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
                                    if extra.getShellType() in config2.schematic.shell_list or config2.schematic.tank_cls & tag_ or veh_name_ in config2.schematic.tanklist:  # isShellGold()
                                        if target_id != BigWorld.player().playerVehicleID:
                                            config0.id_list.append(str(target_id))
                                    BigWorld.callback(0, AUTO_add)
            return


@run_before(PlayerAvatar, '_PlayerAvatar__onArenaPeriodChange')
def autoKeyPressed(_, period, __, ___, ____):
    if period == ARENA_PERIOD.BATTLE:
        conf1_data = config1.getData()
        if conf1_data['enabled'] and conf1_data['auto_key_pressed'] and conf1_data['activeMode']:
            config1.pressed_key()
            return
        conf2_data = config2.getData()
        if conf2_data['enabled'] and conf2_data['auto_key_pressed'] and conf2_data['activeMode']:
            config2.pressed_key()
            return


# not clickable
g_modsListApi.updateModification('modsSettingsApi', enabled=False)

config0 = ConfigInterface()
config1 = ConfigInterface2()
config2 = ConfigInterface3()

if config0.data['extended'] and config0.data['enabled']:
    CONTACT_LIMIT.ROSTER_MAX_COUNT = config0.data['friends']
    CONTACT_LIMIT.BLOCK_MAX_COUNT = config0.data['ignored']
