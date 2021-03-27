# -*- coding: utf-8 -*-
import BigWorld
import Keys
from PYmodsCore import PYmodsConfigInterface,checkKeys
from PYmodsCore.delayed.support import ConfigInterface as CI
from PYmodsCore.config.interfaces.PyMods import PYmodsSettingContainer
from gui.modsListApi import g_modsListApi


class ConfigInterface(PYmodsConfigInterface):
    def __init__(self):
        super(ConfigInterface, self).__init__()

    def init(self):
        self.ID = 'X_Auto_BL_2'
        self.version = '1.31 (10.02.2021)'
        self.data = {'enabled': True,
                     'name': 'HE + blacklist teams',
                     'shell_AP': False,
                     'shell_APCR': False,
                     'shell_HEAT': False,
                     'shell_HE': False,
                     'random': False,
                     'random_key': False,
                     'ranked': False,
                     'ranked_key': False,
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
                     'spg': False,
                     'spg_key': False,
                     'tanklist': [None],
                     'auto_key_pressed': False,
                     'wheeled': False,
                     'wheeled_key': False}
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
            'UI_setting_random_tooltip': 'This selects and shows the current mode.',
            'UI_setting_random_key_text': 'Random key',
            'UI_setting_random_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_ranked_text': 'Ranked',
            'UI_setting_ranked_tooltip': 'This selects and shows the current mode.',
            'UI_setting_ranked_key_text': 'Ranked key',
            'UI_setting_ranked_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_other_modes_text': 'Other modes',
            'UI_setting_other_modes_tooltip': 'This selects and shows the current mode.',
            'UI_setting_other_modes_key_text': 'Other modes key',
            'UI_setting_other_modes_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_light_text': 'Light',
            'UI_setting_light_tooltip': 'This selects and shows the current mode.',
            'UI_setting_light_key_text': 'Light key',
            'UI_setting_light_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_med_text': 'Medium',
            'UI_setting_med_tooltip': 'This selects and shows the current mode.',
            'UI_setting_med_key_text': 'Medium key',
            'UI_setting_med_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_heavy_text': 'Heavy',
            'UI_setting_heavy_tooltip': 'This selects and shows the current mode.',
            'UI_setting_heavy_key_text': 'Heavy key',
            'UI_setting_heavy_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_td_text': 'TD',
            'UI_setting_td_tooltip': 'This selects and shows the current mode.',
            'UI_setting_td_key_text': 'TD key',
            'UI_setting_td_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_spg_text': 'Arty',
            'UI_setting_spg_tooltip': 'This selects and shows the current mode.',
            'UI_setting_spg_key_text': 'Arty key',
            'UI_setting_spg_key_tooltip': 'This selects and shows the current mode.',
            'UI_setting_auto_key_pressed_text': 'Auto key pressed',
            'UI_setting_auto_key_pressed_tooltip': 'This selects and shows the current mode.',
            'UI_setting_wheeled_text': 'Wheeled',
            'UI_setting_wheeled_tooltip': 'This selects and shows the current mode.',
            'UI_setting_wheeled_key_text': 'Wheeled key',
            'UI_setting_wheeled_key_tooltip': 'This selects and shows the current mode.'
        }
        super(ConfigInterface, self).init()
        self.containerClass = MyPYmodsSettingContainer

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
                            self.tb.createControl('shell_HEAT')],
                'column2': [self.tb.createEmpty(),
                            self.tb.createEmpty(),
                            self.tb.createEmpty(),
                            self.tb.createControl('auto_key_pressed'),
                            self.tb.createControl('random_key'),
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


class MyPYmodsSettingContainer(PYmodsSettingContainer):
    def init(self):
        super(MyPYmodsSettingContainer, self).init()
        self.i18n = {
            'modsListApiName': "Blacklist mod",
            'modsListApiDescription': "Extended automated blacklist modification settings",
            'windowTitle': "Blacklist mod settings",
            'enableButtonTooltip': '{HEADER}ON/OFF{/HEADER}{BODY}Enable/disable this mod{/BODY}'}


# not clickable
g_modsListApi.updateModification('modsSettingsApi', enabled=False)

_config = ConfigInterface()
