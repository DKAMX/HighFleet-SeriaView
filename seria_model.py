# from ast import literal_eval
from copy import deepcopy
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

    @classmethod
    def get_ammo_index(cls, name: str) -> str:
        for ammo in cls:
            if ammo.value[1] == name:
                return ammo.value[0]
        return '0'

    @classmethod
    def get_ammo_types(cls) -> list:
        return [ammo.value[1] for ammo in cls]


class AmmoModel:
    def __init__(self, seria: SeriaNode):
        '''Create an AmmoModel from an existing SeriaNode'''

        self.seria: SeriaNode = seria
        self.index: str = seria.get_attribute('m_index')
        self.count: str = seria.get_attribute('m_count')

    @classmethod
    def from_index(self, index: str, count: str):
        '''Create an AmmoModel from scratch
        @return: AmmoModel'''

        seria = SeriaNode(f'm_items={ITEM_AMMO_CODE}', 'Item')
        seria.set_attribute('m_classname', 'Item')
        seria.set_attribute('m_code', ITEM_AMMO_CODE)
        seria.set_attribute('m_index', index)
        seria.set_attribute('m_count', count)

        return AmmoModel(seria)

    def set_amount(self, amount: int):
        '''Ammo model itself don't handle 0 amount because it cannot remove itself'''
        if amount <= 0:
            raise ValueError('Amount must be a positive integer')
        else:
            self.seria.set_attribute('m_count', str(amount))
            self.count = str(amount)


class ShipModel:
    def __init__(self, seria: SeriaNode):
        self.seria = seria
        self.creature = seria.get_node_by_class('Frame').get_node_if(
            lambda n: n.get_attribute('m_name') == 'COMBRIDGE').get_node_by_class('Creature')
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
        self.inventory = seria.get_node_if(
            lambda n: n.header == 'm_inventory=7')

        self.name = seria.get_attribute('m_name')
        # total = literal_eval(self.seria.get_attribute('m_tele_fuel_total'))
        # capacity = literal_eval(
        #     self.seria.get_attribute('m_tele_fuel_capacity'))
        # self.fuel_pct = int(total / capacity * 100)

        x = float(self.seria.get_attribute('m_position.x') or 0)
        y = float(self.seria.get_attribute('m_position.y') or 0)
        self.position = (x, y)

    # def add_fuel(self):
    #     for ship in self.ships:
    #         ShipModel(ship).add_fuel()
    #     self.fuel_pct = 100

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

    def get_items(self):
        '''Get the items in the inventory
        @return: a list of tuples containing the item oid and count'''

        items = []
        for item in self.inventory.get_nodes():
            oid = item.get_attribute('m_oid')
            count = item.get_attribute('m_count') or '1'
            items.append((oid, count))
        return items

    def get_item(self, item_oid: str):
        '''Check if the inventory has an item with the specified oid'''

        return self.inventory.get_node_if(lambda n: n.get_attribute('m_oid') == item_oid)

    def set_item(self, index: int, amount: str) -> bool:
        '''set the amount of item in the inventory, based on its appearance order'''

        try:
            amount_value = int(amount)
            if amount_value <= 0:
                raise ValueError('Amount must be a positive integer')
        except ValueError:
            return False

        item = self.inventory.get_node(index)
        if item.has_attribute('m_count'):
            item.set_attribute('m_count', amount)
        else:
            item.put_attribute_after('m_count', amount, 'm_oid')

        return True

    def add_item(self, unique_ids: set, item_node: SeriaNode, amount: int):
        '''Add an item to the inventory, assume the item_node is valid and has no m_count initially'''

        # check if the item already exists
        item = self.get_item(item_node.get_attribute('m_oid'))
        if item:
            count = item.get_attribute('m_count') or '1'
            item.set_attribute('m_count', str(int(count) + amount))
            return

        new_id = max(unique_ids) + 1
        unique_ids.add(new_id)

        item_node_cpy = deepcopy(item_node)
        item_node_cpy.update_attribute('m_id', str(new_id))
        item_node_cpy.set_attribute('m_master_id',
                                    self.inventory.get_attribute('m_id'))
        if amount > 1:
            item_node_cpy.set_attribute('m_count', str(amount))
        else:
            item_node_cpy.set_attribute('m_count', '1')
        self.inventory.add_node(item_node_cpy)

    def add_ship(self, unique_ids: set, next_creature_id: str, ship_node: SeriaNode):
        '''Add a ship to the fleet, assume the ship_node is valid'''

        ship_node_cpy = deepcopy(ship_node)

        next_id = max(unique_ids) + 1
        unique_ids.add(next_id)

        alignment = self.seria.get_attribute('m_alignment')
        escadra_id = self.seria.get_attribute('m_id')
        # make new escadra index for the new ship
        escadra_indexes = set()
        for ship in self.ships:
            # Frame > Body > Creature
            creature = ship.get_node_by_class('Frame').get_node_if(
                lambda n: n.get_attribute('m_name') == 'COMBRIDGE').get_node_by_class('Creature')
            escadra_indexes.add(int(creature.get_attribute('m_escadra_index')))

        cfg_ship_for_adding(ship_node_cpy, unique_ids,
                            next_creature_id, alignment,
                            escadra_id, str(max(escadra_indexes) + 1))

        self.seria.put_node_after(ship_node_cpy, self.ships[-1])
        self.ships.append(ship_node_cpy)


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
        self.seria_node: SeriaNode = None
        self.unique_ids: set = None
        self.ship_unlocks: list = None
        self.scores: int = 0
        self.cash: int = 0
        self.player_squadrons: list = None
        self.npcs: list = None
        self.ammo_list: list = None

    def load(self, seria: SeriaNode):
        self.seria_node = seria
        self.unique_ids = get_unique_ids(seria)
        self.ship_unlocks = get_ship_unlocks(seria)
        self.scores = int(seria.get_attribute('m_scores') or 0)
        self.cash = int(seria.get_attribute('m_cash') or 0)
        escadras = seria.get_nodes_by_class('Escadra')
        self.player_squadrons = [FleetModel(fleet)
                                 for fleet in escadras if fleet.get_attribute('m_alignment') == '1']
        self.npcs = [NpcModel(npc) for npc in seria.filter_nodes(lambda n: n.header == 'm_npcs=68719476739' and (
            n.has_attribute('m_tarkhan') or n.has_attribute('m_joined')))]
        self.ammo_list = [AmmoModel(ammo)
                          for ammo in seria.get_nodes_by_class('Item')]

    def clear(self):
        self.seria_node = None
        self.unique_ids = None
        self.ship_unlocks = None
        self.scores = 0
        self.cash = 0
        self.player_squadrons = None
        self.npcs = None
        self.ammo_list = None

    def get_ammo_list(self):
        if self.ammo_list is None:
            return []

        return [(Ammo.get_ammo_type(ammo.index), ammo.count) for ammo in self.ammo_list]

    def get_ammo_count(self, ammo_index: str) -> str:
        '''Get the amount of ammo of a certain type.
        @return: The amount of ammo, or 0 if the ammo does not exist'''

        if self.ammo_list is None:
            return '0'

        for ammo in self.ammo_list:
            if ammo.index == ammo_index:
                return ammo.count

        return '0'

    def set_ammo(self, index: str, amount: str) -> bool:
        '''Set the amount of ammo of a certain type.
        If the ammo does not exist, it is created.
        @return: True if the operation was successful, False otherwise'''

        if self.ammo_list is None:
            return False

        try:
            amount_value = int(amount)

            if amount_value <= 0:
                return False
            else:
                for ammo in self.ammo_list:
                    # existing ammo
                    if ammo.index == index:
                        ammo.set_amount(amount_value)
                        return True

                # new ammo
                new_ammo = AmmoModel.from_index(index, amount)
                self.ammo_list.append(new_ammo)
                self.seria_node.put_node_before_index(new_ammo.seria, -1)

                return True
        except ValueError:
            return False

    def get_bonus(self):
        if self.seria_node is None:
            return

        return str(self.scores)

    def set_bonus(self, bonus: str):
        if self.seria_node is None:
            return

        try:
            bonus_value = int(bonus)
            if bonus_value < 0:
                raise ValueError('Bonus must be a positive integer')
        except ValueError:
            return

        # has_attribute check for first callback triggered in initialize the entry value
        if bonus_value == 0 and self.seria_node.has_attribute('m_scores'):
            self.seria_node.del_attribute('m_scores')
        else:
            if self.seria_node.has_attribute('m_scores'):
                self.seria_node.set_attribute('m_scores', bonus)
            else:
                self.seria_node.put_attribute_after(
                    'm_scores', bonus, 'm_savetime')

        self.scores = bonus

    def get_money(self):
        if self.seria_node is None:
            return

        return str(self.cash)

    def set_money(self, money: str):
        if self.seria_node is None:
            return

        try:
            money_value = int(money)
            if money_value < 0:
                raise ValueError('Money must be a positive integer')
        except ValueError:
            return

        if money_value == 0 and self.seria_node.has_attribute('m_cash'):
            self.seria_node.remove_attribute('m_cash')
        else:
            if self.seria_node.has_attribute('m_cash'):
                self.seria_node.set_attribute('m_cash', money)
            else:
                self.seria_node.put_attribute_before(
                    'm_cash', money, 'm_npc_index')

        self.cash = money

    def get_worldview(self, attribute: str):
        if self.seria_node is None:
            return

        return self.seria_node.get_attribute(f'm_char_{attribute}_val') or '0'

    def set_worldview(self, attribute: str, value: str):
        if self.seria_node is None:
            return

        name_value_disaplay = f'm_char_{attribute}'
        name_value = f'm_char_{attribute}_val'
        value_disaplay = str(int(float(value)))
        if self.seria_node.has_attribute(name_value_disaplay):
            self.seria_node.set_attribute(name_value_disaplay, value_disaplay)
            self.seria_node.set_attribute(name_value, value)
        else:
            self.seria_node.put_attribute_after(
                name_value_disaplay, value, 'm_radio_duration_base')
            self.seria_node.put_attribute_after(
                name_value, value_disaplay, name_value_disaplay)

    def get_squadron(self, index: int):
        if self.player_squadrons is None:
            return

        return self.player_squadrons[index]

    def next_creature_id(self):
        '''Get the next creature id for adding a new ship, will increment the id while return'''
        if self.seria_node is None:
            return None

        id = self.seria_node.get_attribute('nextCreatureId')
        print(id)
        self.seria_node.set_attribute('nextCreatureId', str(int(id) + 1))

        return id

    def unlock_all_ships(self):
        if self.seria_node is None:
            return

        for i, unlock in enumerate(self.ship_unlocks):
            self.ship_unlocks[i] = (unlock[0], True)

        self.seria_node.set_attribute(
            'm_unlocks', [f'{name}|{int(unlocked)}' for name, unlocked in self.ship_unlocks])


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


def get_ship_name(node: SeriaNode):
    '''Get the ship name from a ship node
    @return: The ship name, or None if the node is not a ship'''

    try:
        frame = node.get_node_by_class('Frame')
        body = frame.get_node_if(
            lambda n: n.get_attribute('m_name') == 'COMBRIDGE')
        creature = body.get_node_by_class('Creature')
        return creature.get_attribute('m_ship_name')
    except:
        return None


def get_node_attr_text(node: SeriaNode) -> str:
    '''Get the attributes of a node as a list of tuples
    @return: a list of key-value pairs in text format'''

    output = ''
    for key, value in node.get_attributes().items():
        if isinstance(value, list):
            for v in value:
                output += f'{key}={v}\n'
        else:
            output += f'{key}={value}\n'
    return output


def get_part_oid_set(node: SeriaNode) -> set:
    '''Get oid of part that is available in the game (m_important=true)
    @return set of oid'''

    if node is None or node.get_attribute('m_classname') != 'ObjectsLibrary':
        return

    parts = set()
    for child in node.get_nodes():
        if child.has_attribute('m_important'):
            parts.add(child.get_attribute('m_oid'))
    return parts

    # FIXME missing oids like ITEM_HULL


def cfg_ship_for_adding(ship_node: SeriaNode, unique_ids: set, next_creature_id: str, alignment: str, escadra_id: str, escadra_index: str):
    next_id = max(unique_ids) + 1
    unique_ids.add(next_id)

    # update ship design with needed attributes obtained from profile
    ship_node.header = 'm_children=7'
    ship_node.put_attribute_after('m_state', '2', 'm_name')
    ship_node.put_attribute_after('m_master_id', escadra_id, 'm_state')

    # m_id for root Node node of the ship
    ship_node.update_attribute('m_id', str(next_id))

    # update all depth 2 nodes with new m_id
    for node in ship_node.get_nodes():
        old_id = node.get_attribute('m_id')

        next_id += 1
        unique_ids.add(next_id)
        node.update_attribute('m_id', str(next_id))
        # update all joint nodes with new m_id reference
        for node in ship_node.get_nodes():
            node.update_attribute_by_value(old_id, str(next_id))

    ship_frame = ship_node.get_node_by_class('Frame')

    next_id += 1
    unique_ids.add(next_id)
    ship_frame.update_attribute('m_id', str(next_id))

    # update all depth 3 nodes in frame node with new m_id
    for node in ship_frame.get_nodes():
        old_id = node.get_attribute('m_id')

        next_id += 1
        unique_ids.add(next_id)
        node.update_attribute('m_id', str(next_id))

        # update all joint nodes with new m_id reference
        for node in ship_node.get_nodes():
            node.update_attribute_by_value(old_id, str(next_id))

    ship_creature = ship_frame.get_node_if(lambda n: n.get_attribute(
        'm_name') == 'COMBRIDGE').get_node_by_class('Creature')

    next_id += 1
    unique_ids.add(next_id)
    old_creature_id = ship_creature.get_attribute('m_id')
    ship_creature.update_attribute('m_id', str(next_id))
    ship_creature.set_attribute('m_owner_id', str(next_id))
    ship_node.update_attribute_by_value(old_creature_id, str(next_id))

    ship_creature.set_attribute('creatureId', next_creature_id)

    ship_creature.put_attribute_after('m_escadra.id', escadra_id,
                                      'm_health_lock')
    ship_creature.put_attribute_after('m_escadra_index', escadra_index,
                                      'm_escadra.id')
    ship_creature.put_attribute_after('m_alignment', alignment,
                                      'm_playable')
    ship_creature.put_attribute_after('m_tarkhan', 'DAUD',  # enemy don't have tarkhan
                                      'm_alignment')
    ship_creature.put_attribute_after('m_radiation_extra', '1',
                                      'm_tarkhan')

    crew_capacity = ship_creature.get_attribute(
        'm_tele_crew_capacity')
    ship_creature.put_attribute_before('m_tele_crew_total', crew_capacity,
                                       'm_tele_crew_capacity')
    ship_creature.put_attribute_before('m_moral', '10',
                                       'creatureId')
    ship_creature.put_attribute_before('m_rad_seekness_timer', '5',
                                       'shipLoadTime')
    ship_creature.put_attribute_before('shipLoadTime', '0',
                                       'm_tele_fuel_on')

    ship_creature.set_attribute('wasAddedToPlayerEscadra', 'true')
