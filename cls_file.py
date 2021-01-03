from constants import ARENA_BONUS_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME


class SHELL_TYPES(object):
    HOLLOW_CHARGE = 'HOLLOW_CHARGE'
    HIGH_EXPLOSIVE = 'HIGH_EXPLOSIVE'
    ARMOR_PIERCING = 'ARMOR_PIERCING'
    ARMOR_PIERCING_HE = 'ARMOR_PIERCING_HE'
    ARMOR_PIERCING_CR = 'ARMOR_PIERCING_CR'
    SMOKE = 'SMOKE'


class GlobalVars(object):
    def __init__(self):
        self.all_modes = []
        self.active_idx = 0
        self.active_mode = self.all_modes[self.active_idx] if self.all_modes else None
        self.ignored = 1000000
        self.friends = 1000000
        self.extended = False
        self.config_data = {}
        self.check_running = False
        self.id_list = []

    def increment_mode(self):
        if self.all_modes:
            nr_modes = len(self.all_modes)
            if self.active_idx + 1 == nr_modes:
                self.active_idx = 0
                self.active_mode = self.all_modes[self.active_idx]
            else:
                self.active_idx += 1
                self.active_mode = self.all_modes[self.active_idx]

    def loadFromDict(self, settingsDict):
        pass


class SchematicForMode(object):
    other_game_modes = (0, 2, 4, 5, 6, 7, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                        26, 27, 28, 29, 30, 31, 33)

    def __init__(self, name='', shell_AP=None, shell_APCR=None, shell_HEAT=None,
                 shell_HE=None, random=ARENA_BONUS_TYPE.REGULAR, random_key=ARENA_BONUS_TYPE.REGULAR,
                 andere_modi=None, andere_modi_key=None, light=None, light_key=None,
                 med=None, med_key=None, heavy=None, heavy_key=None, td=None, td_key=None, spg=None,
                 spg_key=None, tanklist=None):
        self.name = name
        self.shell_list = {shell_AP, shell_APCR, shell_HEAT, shell_HE}
        self.auto_mode = {random, andere_modi}  # andere_modi must be tuple
        self.key_mode = {random_key, andere_modi_key}
        self.tank_cls = {light, med, heavy, td, spg}
        self.tank_cls_key = {light_key, med_key, heavy_key, td_key, spg_key}
        self.tanklist = tanklist


def std_name(all_modes):
    if all_modes:
        all_modes_names = [modes.name for modes in all_modes]
        start_nr = 1
        basic_name = 'Mode '
        start_name = basic_name + str(start_nr)
        while start_name in all_modes_names:
            start_nr += 1
            start_name = basic_name + str(start_nr)
        return start_name


global_vars = GlobalVars()
disabled_mode = SchematicForMode(name='Mod disabled', random=None, random_key=None)
arty_mode = SchematicForMode(name='Only arty', andere_modi=SchematicForMode.other_game_modes,
                             andere_modi_key=SchematicForMode.other_game_modes, spg=VEHICLE_CLASS_NAME.SPG,
                             spg_key=VEHICLE_CLASS_NAME.SPG)
he_mode = SchematicForMode(name='Only HE', shell_HE=SHELL_TYPES.HIGH_EXPLOSIVE, random_key=None,
                           andere_modi=SchematicForMode.other_game_modes)
he_bl_mode = SchematicForMode(name='HE + blacklist teams', shell_HE=SHELL_TYPES.HIGH_EXPLOSIVE,
                              andere_modi=SchematicForMode.other_game_modes,
                              andere_modi_key=SchematicForMode.other_game_modes)
