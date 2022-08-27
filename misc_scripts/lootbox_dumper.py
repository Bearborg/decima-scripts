import os

import pydecima
from pydecima.resources import EntityResource, InventoryEntityResource, InventoryItemComponentResource, \
    InventoryLootPackageComponentResource, LootData, LootItem, LootSlot

game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')
script_objects = {}


def recurse_loot(loot, level=0):
    indent_char = ' '
    if loot.type == 'InventoryLootPackageComponentResource':
        loot: InventoryLootPackageComponentResource
        inv_name = x.inventory_item_component.follow(script_objects).item_name.follow(script_objects)
        print('{}package {} ({}):'.format(indent_char * level, loot.name, inv_name))
        for item in loot.loot_slot:
            recurse_loot(item.follow(script_objects), level + 1)
    elif loot.type == 'LootSlot':
        loot: LootSlot
        print('{}slot {}:'.format(indent_char * level, loot.name))
        for item in loot.loot_data:
            recurse_loot(item.follow(script_objects), level + 1)
    elif loot.type == 'LootData':
        loot: LootData
        print('{}data {} ({:n}% chance, x{}, unk3={}):'.format(indent_char * level, loot.name, loot.probability,
              loot.quantity, loot.unk3))
        for item in loot.loot_item:
            recurse_loot(item.follow(script_objects), level + 1)
    elif loot.type == 'LootItem':
        loot: LootItem
        print('{}item {} (unk={:n}, unk2={}):'.format(indent_char * level, loot.name, loot.unk, loot.unk2))
        recurse_loot(loot.inventoryEntity.follow(script_objects), level + 1)
    elif loot.type == 'InventoryEntityResource':
        loot: InventoryEntityResource
        print('{}invEntity {}'.format(indent_char * level, loot.name))
        for item in loot.ref_list:
            ref_val = item.follow(script_objects)
            if ref_val.type == 'InventoryItemComponentResource':
                print('{}invItem {}'.format(indent_char * (level + 1), ref_val.item_name.follow(script_objects)))
    elif loot.type == 'EntityResource':
        loot: EntityResource
        print('{}entity {}'.format(indent_char * level, loot.name))
        for item in loot.ref_list:
            ref_val: InventoryItemComponentResource = item.follow(script_objects)
            if ref_val.type == 'InventoryItemComponentResource':
                print('{}invItem {} (unk={}, unkShort={})'.format(indent_char * (level + 1),
                                                                  ref_val.item_name.follow(script_objects),
                                                                  ref_val.unk,
                                                                  ref_val.unk_short))
    else:
        print('{}{}'.format(indent_char * level, loot))


pydecima.reader.set_globals(_game_root_file=game_root_file, _decima_version='HZDPC')
base_game_box_file = os.path.join(pydecima.reader.game_root, r'entities/shops/items_econ/econ_items.core')
dlc_box_file = os.path.join(pydecima.reader.game_root, r'entities/dlc1/economy/dlc1_loot_items.core')
pydecima.reader.read_objects(base_game_box_file, script_objects)
pydecima.reader.read_objects(dlc_box_file, script_objects)

for x in script_objects.copy().values():
    if x.type == 'InventoryLootPackageComponentResource':
        recurse_loot(x)
