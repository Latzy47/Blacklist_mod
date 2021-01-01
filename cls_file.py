from constants import ARENA_BONUS_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME


class SHELL_TYPES(object):
    HOLLOW_CHARGE = 'HOLLOW_CHARGE'
    HIGH_EXPLOSIVE = 'HIGH_EXPLOSIVE'
    ARMOR_PIERCING = 'ARMOR_PIERCING'
    ARMOR_PIERCING_HE = 'ARMOR_PIERCING_HE'
    ARMOR_PIERCING_CR = 'ARMOR_PIERCING_CR'
    SMOKE = 'SMOKE'


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


class GlobalCls(object):
    all_modes = []
    active_idx = 0
    active_mode = all_modes[active_idx] if all_modes else None

    @staticmethod
    def increment_mode():
        nr_modes = len(GlobalCls.all_modes)
        if GlobalCls.active_idx + 1 == nr_modes:
            GlobalCls.active_idx = 0
            GlobalCls.active_mode = GlobalCls.all_modes[GlobalCls.active_idx]
        elif nr_modes != 0:
            GlobalCls.active_idx += 1
            GlobalCls.active_mode = GlobalCls.all_modes[GlobalCls.active_idx]


class Schematic(object):
    def __init__(self, name=std_name(GlobalCls.all_modes), shell_AP=None, shell_APCR=None, shell_HEAT=None,
                 shell_HE=None, random=ARENA_BONUS_TYPE.REGULAR, random_key=ARENA_BONUS_TYPE.REGULAR,
                 andere_modi=True, andere_modi_key=True, light=None, light_key=None,
                 med=None, med_key=None, heavy=None, heavy_key=None, td=None, td_key=None, spg=None,
                 spg_key=None, tanklist=None):
        self.name = name
        self.shell_list = {shell_AP, shell_APCR, shell_HEAT, shell_HE}
        self.auto_mode = {random, andere_modi}
        self.key_mode = {random_key, andere_modi_key}
        self.tank_cls = {light, med, heavy, td, spg}
        self.tank_cls_key = {light_key, med_key, heavy_key, td_key, spg_key}
        self.tanklist = tanklist
