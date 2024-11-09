from ast import literal_eval
from enum import Enum
from seria import SeriaNode

ITEM_AMMO_CODE = '2199023255555'
FUEL_CAPACITY = {'MDL_FUEL_01': '35000', 'MDL_FUEL_02': '400000'}


class Ammo(Enum):
    ROCKET_122 = ('8', '122mm Unguided rocket')
    ROCKET_340 = ('13', '340mm Unguided rocket')
    SHELL_37_I = ('14', '37mm Incendiary')
    SHELL_57_I = ('15', '57mm Incendiary')
    SHELL_100_AP = ('16', '100mm Armor piercing')
    SHELL_100_PF = ('17', '100mm Proximity fuze')
    SHELL_100_I = ('18', '100mm Incendiary')
    SHELL_130_AP = ('19', '130mm Armor piercing')
    SHELL_130_PF = ('20', '130mm Proximity fuze')
    SHELL_130_I = ('21', '130mm Incendiary')
    SHELL_130_LG = ('22', '130mm Laser guided')
    SHELL_180_AP = ('23', '180mm Armor piercing')
    SHELL_180_PF = ('24', '180mm Proximity fuze')
    SHELL_180_I = ('25', '180mm Incendiary')
    SHELL_180_LG = ('26', '180mm Laser guided')
    ROCKET_220_I = ('27', '220mm Incendiary')
    SHELL_300_I = ('28', '300mm Incendiary')
    BOMB_100 = ('30', '100 kg General purpose bomb')
    BOMB_250 = ('31', '250 kg General purpose bomb')
    MISSILE_AA = ('35', 'Air-to-air missile')

    @classmethod
    def get_ammo_type(cls, index: str) -> str:
        for ammo in cls:
            if ammo.value[0] == index:
                return ammo.value[1]
        return f'Unknown {index}'


class AmmoModel:
    def __init__(self, seria: SeriaNode):
        '''Create an AmmoModel from an existing SeriaNode'''

        self.seria = seria
        self.type = Ammo.get_ammo_type(seria.get_attribute('m_index'))
        self.amount = int(seria.get_attribute('m_count'))

    @classmethod
    def from_index(ammo_index: int, amount: int):
        '''Create an AmmoModel from scratch
        @return: AmmoModel'''

        seria = SeriaNode(f'm_items={ITEM_AMMO_CODE}', 'Item')
        seria.set_attribute('m_classname', 'Item')
        seria.set_attribute('m_code', ITEM_AMMO_CODE)
        seria.set_attribute('m_index', str(ammo_index))
        seria.set_attribute('m_count', str(amount))

        return AmmoModel(seria)

    def set_amount(self, amount: int):
        if amount <= 0:
            raise ValueError('Amount must be a positive integer')
        else:
            self.seria.set_attribute('m_count', str(amount))


class ShipModel:
    def __init__(self, seria: SeriaNode):
        self.seria = seria
        self.creature = seria.get_node_by_class(
            'Frame').get_node(0).get_node(0)
        self.moral = int(self.creature.get_attribute('m_moral'))

    def add_fuel(self):
        fuel_nodes = self.seria.get_node_by_class('Frame').filter_nodes(
            lambda n: n.get_attribute('m_name') == 'FUEL')
        for node in fuel_nodes:
            oid = node.get_attribute('m_oid')
            node.put_attribute_before(
                'm_mdl_fuel', FUEL_CAPACITY[oid], 'm_rescue_flameable')

    def set_moral(self, moral: int):
        if moral < 1 or moral > 10:
            raise ValueError('Moral must be between 1 and 10')
        self.creature.set_attribute('m_moral', str(moral))
        self.moral = moral


class FleetModel:
    def __init__(self, seria: SeriaNode):
        self.seria = seria
        self.ships = seria.filter_nodes(
            lambda n: n.header == 'm_children=7')

        total = literal_eval(self.seria.get_attribute('m_tele_fuel_total'))
        capacity = literal_eval(
            self.seria.get_attribute('m_tele_fuel_capacity'))
        self.fuel_pct = int(total / capacity * 100)

        x = int(self.seria.get_attribute('m_position.x') or 0)
        y = int(self.seria.get_attribute('m_position.y') or 0)
        self.position = (x, y)

    def add_fuel(self):
        for ship in self.ships:
            ShipModel(ship).add_fuel()
        self.fuel_pct = 100

    def set_position(self, x: int, y: int):
        if self.seria.has_attribute('m_position.x'):
            self.seria.set_attribute('m_position.x', str(x))
        else:
            self.seria.put_attribute_after('m_position.x', str(x), 'm_name')

        if self.seria.has_attribute('m_position.y'):
            self.seria.set_attribute('m_position.y', str(y))
        else:
            self.seria.put_attribute_after(
                'm_position.y', str(y), 'm_position.x')

        self.position = (x, y)


class NpcModel:
    def __init__(self, seria: SeriaNode):
        self.seria = seria
        self.name = seria.get_attribute('m_name')
        self.fullname = seria.get_attribute('m_fullname')
        # assume NPC is tarkhan thus don't store m_tarkhan
        self.joined = bool(seria.get_attribute('m_joined')) or False
        self.location = seria.get_attribute('m_location')
        self.loyalty = int(seria.get_attribute('m_loyalty') or 0)

    def set_loyalty(self, loyalty: int):
        if loyalty < 1 or loyalty > 12:
            raise ValueError('Loyalty must be between 1 and 12')
        self.seria.set_attribute('m_loyalty', str(loyalty))
        self.loyalty = loyalty


class ProfileModel:
    def __init__(self):
        self.seria: SeriaNode = None
        self.unique_ids: set = None
        self.ship_unlocks: list = None
        self.scores: int = 0
        self.cash: int = 0
        escadras: list = None
        self.player_fleets: list = None
        self.npcs: list = None
        self.ammo_list: list = None

    def load(self, seria: SeriaNode):
        self.seria = seria
        self.unique_ids = get_unique_ids(seria)
        self.ship_unlocks = get_ship_unlocks(seria)
        self.scores = int(seria.get_attribute('m_scores') or 0)
        self.cash = int(seria.get_attribute('m_cash') or 0)
        escadras = seria.get_nodes_by_class('Escadra')
        self.player_fleets = [FleetModel(fleet)
                              for fleet in escadras if fleet.get_attribute('m_alignment') == '1']
        self.npcs = [NpcModel(npc) for npc in seria.filter_nodes(lambda n: n.header == 'm_npcs=68719476739' and (
            n.has_attribute('m_tarkhan') or n.has_attribute('m_joined')))]
        self.ammo_list = [AmmoModel(ammo)
                          for ammo in seria.get_nodes_by_class('Item')]

    def get_ammo_list(self):
        if self.ammo_list is None:
            return []

        return [(ammo.type, ammo.amount) for ammo in self.ammo_list]

    def set_ammo(self, ammo_index: str, amount: int):
        '''Set the amount of ammo of a certain type.
        If the amount is 0, the ammo is removed.
        If the ammo does not exist, it is created.'''

        if self.ammo_list is None:
            return

        if amount < 0:
            raise ValueError('Amount must be a positive integer')
        if amount == 0:
            ammo_list = self.seria.get_nodes_by_class('Item')
            for ammo in ammo_list:
                if ammo.get_attribute('m_index') == ammo_index:
                    self.seria.del_node(ammo.seria)
                    return
        else:
            ammo_list = self.seria.get_nodes_by_class('Item')
            for ammo in ammo_list:
                # existing ammo
                if ammo.get_attribute('m_index') == ammo_index:
                    ammo.set_amount(str(amount))
                    return
            # new ammo
            new_ammo = AmmoModel(ammo_index, amount)
            self.ammo_list.append(new_ammo)
            self.seria.put_node_before_index(new_ammo.seria, -1)

    def get_bonus(self):
        if self.seria is None:
            return

        return str(self.scores)

    def set_bonus(self, bonus: str):
        if self.seria is None:
            return

        try:
            bonus_value = int(bonus)
            if bonus_value < 0:
                raise ValueError('Bonus must be a positive integer')
        except ValueError:
            return

        # has_attribute check for first callback triggered in initialize the entry value
        if bonus_value == 0 and self.seria.has_attribute('m_scores'):
            self.seria.del_attribute('m_scores')
        else:
            if self.seria.has_attribute('m_scores'):
                self.seria.set_attribute('m_scores', bonus)
            else:
                self.seria.put_attribute_after('m_scores', bonus, 'm_savetime')

        self.scores = bonus

    def get_money(self):
        if self.seria is None:
            return

        return str(self.cash)

    def set_money(self, money: str):
        if self.seria is None:
            return

        try:
            money_value = int(money)
            if money_value < 0:
                raise ValueError('Money must be a positive integer')
        except ValueError:
            return

        if money_value == 0 and self.seria.has_attribute('m_cash'):
            self.seria.remove_attribute('m_cash')
        else:
            if self.seria.has_attribute('m_cash'):
                self.seria.set_attribute('m_cash', money)
            else:
                self.seria.put_attribute_before('m_cash', money, 'm_npc_index')

        self.cash = money

    def unlock_all_ships(self):
        if self.seria is None:
            return

        for i, unlock in enumerate(self.ship_unlocks):
            self.ship_unlocks[i] = (unlock[0], True)

        self.seria.set_attribute(
            'm_unlocks', [f'{name}|{int(unlocked)}' for name, unlocked in self.ship_unlocks])

    def get_worldview(self, attribute: str):
        if self.seria is None:
            return

        return self.seria.get_attribute(f'm_char_{attribute}_val') or '0'

    def set_worldview(self, attribute: str, value: str):
        if self.seria is None:
            return

        name_value_disaplay = f'm_char_{attribute}'
        name_value = f'm_char_{attribute}_val'
        value_disaplay = str(int(float(value)))
        if self.seria.has_attribute(name_value_disaplay):
            self.seria.set_attribute(name_value_disaplay, value_disaplay)
            self.seria.set_attribute(name_value, value)
        else:
            self.seria.put_attribute_after(
                name_value_disaplay, value, 'm_radio_duration_base')
            self.seria.put_attribute_after(
                name_value, value_disaplay, name_value_disaplay)


def get_unique_ids(seria: SeriaNode) -> set:
    unique_ids = set()

    id = seria.get_attribute('m_id')
    if id:
        unique_ids.add(int(id))

    for child in seria.get_nodes():
        unique_ids.update(get_unique_ids(child))

    return unique_ids


def get_ship_unlocks(seria: SeriaNode) -> list:
    '''Return a list of tuples containing the ship name and whether it is unlocked
    @return: [(ship_name, unlocked), ...]'''

    ship_unlocks = []

    for item in seria.get_attribute('m_unlocks'):
        unlock = item.split('|')
        ship_unlocks.append((unlock[0], bool(int(unlock[1]))))

    return ship_unlocks
