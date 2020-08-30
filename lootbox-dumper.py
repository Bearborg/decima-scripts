import decima

script_objects = {}


def recurse_loot(loot, level=0):
    indent_char = ' '
    if loot.type == 'InventoryLootPackageComponentResource':
        loot: decima.InventoryLootPackageComponentResource
        inv_name = x.inventory_item_component.follow(script_objects).item_name.follow(script_objects)
        print('{}package {} ({}):'.format(indent_char * level, loot.name, inv_name))
        for item in loot.loot_slot:
            recurse_loot(item.follow(script_objects), level + 1)
    elif loot.type == 'LootSlot':
        loot: decima.LootSlot
        print('{}slot {}:'.format(indent_char * level, loot.name))
        for item in loot.loot_data:
            recurse_loot(item.follow(script_objects), level + 1)
    elif loot.type == 'LootData':
        loot: decima.LootData
        print('{}data {} ({:n}% chance, x{}, unk3={}):'.format(indent_char * level, loot.name, loot.probability,
              loot.quantity, loot.unk3))
        for item in loot.loot_item:
            recurse_loot(item.follow(script_objects), level + 1)
    elif loot.type == 'LootItem':
        loot: decima.LootItem
        print('{}item {} (unk={:n}, unk2={}):'.format(indent_char * level, loot.name, loot.unk, loot.unk2))
        recurse_loot(loot.inventoryEntity.follow(script_objects), level + 1)
    elif loot.type == 'InventoryEntityResource':
        loot: decima.InventoryEntityResource
        print('{}invEntity {}'.format(indent_char * level, loot.name))
        for item in loot.ref_list:
            ref_val = item.follow(script_objects)
            if ref_val.type == 'InventoryItemComponentResource':
                print('{}invItem {}'.format(indent_char * (level + 1), ref_val.item_name.follow(script_objects)))
    elif loot.type == 'EntityResource':
        loot: decima.EntityResource
        print('{}entity {}'.format(indent_char * level, loot.name))
        for item in loot.ref_list:
            ref_val: decima.InventoryItemComponentResource = item.follow(script_objects)
            if ref_val.type == 'InventoryItemComponentResource':
                print('{}invItem {} (unk={}, unkShort={})'.format(indent_char * (level + 1),
                                                                  ref_val.item_name.follow(script_objects),
                                                                  ref_val.unk,
                                                                  ref_val.unk_short))
    else:
        print('{}{}'.format(indent_char * level, loot))


box_file = r'E:\Game Files\HZDCE\Image0\packed_pink\entities\shops\items_econ\econ_items.core'
# box_file = r'E:\Game Files\HZDCE\Image0\packed_pink\entities\dlc1\economy\dlc1_loot_items.core'

decima.read_objects(box_file, script_objects)
# x: InventoryLootPackageComponentResource = script_objects[binascii.a2b_hex('B423B7BE5FE234329211502E3DA5F021')]
for x in script_objects.copy().values():
    if x.type == 'InventoryLootPackageComponentResource':
        recurse_loot(x)
