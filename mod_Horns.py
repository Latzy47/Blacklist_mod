# -*- coding: utf-8 -*-
import Keys
from PYmodsCore import PYmodsConfigInterface, checkKeys
from PYmodsCore.delayed.support import ConfigInterface as CI
from PYmodsCore.config.interfaces.PyMods import PYmodsSettingContainer
from gui.modsListApi import g_modsListApi


class ConfigInterface(PYmodsConfigInterface):
    def __init__(self):
        super(ConfigInterface, self).__init__()

    def init(self):
        self.ID = 'X_Auto_BL'
        self.version = '1.31 (%(file_compile_date)s)'
        self.defaultKeys = {'hotkey1': [Keys.KEY_O, [Keys.KEY_LALT, Keys.KEY_RALT]],
                            'hotkey2': [Keys.KEY_B, [Keys.KEY_LALT, Keys.KEY_RALT]],
                            'hotkey3': [Keys.KEY_O, [Keys.KEY_LCONTROL, Keys.KEY_RCONTROL]],  # useless?
                            'hotkey4': [Keys.KEY_C, [Keys.KEY_LALT, Keys.KEY_RALT]],
                            'hotkey5': [Keys.KEY_X, [Keys.KEY_LALT, Keys.KEY_RALT]]}
        self.data = {'enabled': True,
                     'mode': 3,
                     'ignored': 1000000,
                     'extended': True,
                     'friends': 1000000,
                     'hotkey1': self.defaultKeys['hotkey1'],
                     'hotkey2': self.defaultKeys['hotkey2'],
                     'hotkey3': self.defaultKeys['hotkey3'],
                     'hotkey4': self.defaultKeys['hotkey4'],
                     'hotkey5': self.defaultKeys['hotkey5']}
        self.i18n = {
            'UI_description': 'Extended automated blacklist',
            'UI_setting_mode_text': 'Current mode',
            'UI_setting_mode_tooltip': 'This selects and shows the current mode.',
            'UI_setting_ignored_text': 'Number blacklist',
            'UI_setting_ignored_tooltip': 'This number shows how big your blacklist is.',
            'UI_setting_extended_text': 'Extend lists',
            'UI_setting_extended_tooltip': 'This enables/disables the extention of the blacklist and friendlist.\n'
                                           'Restarting the game is required to take effect.',
            'UI_setting_friends_text': 'Number friendlist',
            'UI_setting_friends_tooltip': 'This number shows how big your friendlist is.',
            'UI_setting_hotkey1_text': 'Hotkey',
            'UI_setting_hotkey1_tooltip': 'This is a hotkey.',
            'UI_setting_hotkey2_text': 'Hotkey',
            'UI_setting_hotkey2_tooltip': 'This is a hotkey.',
            'UI_setting_hotkey3_text': 'Hotkey',
            'UI_setting_hotkey3_tooltip': 'This is a hotkey.',
            'UI_setting_hotkey4_text': 'Hotkey',
            'UI_setting_hotkey4_tooltip': 'This is a hotkey.',
            'UI_setting_hotkey5_text': 'Hotkey',
            'UI_setting_hotkey5_tooltip': 'This is a hotkey.'}
        super(ConfigInterface, self).init()
        self.containerClass = MyPYmodsSettingContainer

    def createTemplate(self):
        return {'modDisplayName': self.i18n['UI_description'],
                'enabled': self.data['enabled'],
                'column1': [self.tb.createSlider('ignored', 5000, 1000000, 5000),
                            self.tb.createSlider('friends', 5000, 1000000, 5000),
                            self.tb.createHotKey('hotkey1'),
                            self.tb.createHotKey('hotkey3')],
                'column2': [self.tb.createControl('extended'),
                            self.tb.createOptions('mode', [0, 1, 2, 3]),
                            self.tb.createHotKey('hotkey2'),
                            self.tb.createHotKey('hotkey4'),
                            self.tb.createHotKey('hotkey5')]}

    def onButtonPress(self, vName, value):
        pass

    def onMSADestroy(self):
        self.readCurrentSettings()

    def onHotkeyPressed(self, event):
        if event.isKeyDown() and checkKeys(self.data['hotkey2']):
            print 'Test mod_Horns.py ###################'


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


# not clickable
g_modsListApi.updateModification('modsSettingsApi', enabled=False)

_config = ConfigInterface()
