import binascii
import struct
import os
import io
from codecs import iterdecode
from enum import IntEnum, IntFlag
from functools import partial
from itertools import islice

from typing import Dict, BinaryIO, TypeVar, Generic, List, Any, Tuple

game_root_ps4 = r'E:\Game Files\HZDCE\Image0\packed_pink'
game_root_pc = r'E:\Game Files\HZDPC'
is_ps4 = False
T = TypeVar('T')


class Resource:
    def __init__(self, stream: BinaryIO):
        self.type_hash = struct.unpack('Q', stream.read(8))[0]
        littleendian_type = '{0:X}'.format(self.type_hash)
        type_map = ps4_type_map if is_ps4 else pc_type_map
        if littleendian_type in type_map:
            self.type = type_map[littleendian_type][0]
        else:
            self.type = 'Unknown Type'
        self.size = struct.unpack('I', stream.read(4))[0]
        self.uuid = stream.read(16)

    def __str__(self):
        return '{}: {}'.format(self.type, binascii.hexlify(self.uuid).decode('ASCII'))

    def __repr__(self):
        return self.__str__()


class Ref(Generic[T]):
    def __init__(self, stream: BinaryIO):
        self.type: int = struct.unpack('B', stream.read(1))[0]
        if self.type > 0:
            self.hash: bytes = stream.read(16)
        if self.type in [2, 3]:
            self.path: str = parse_hashed_string(stream)

    def follow(self, resource_dict: Dict[bytes, Resource]) -> T:
        if self.type == 0:
            return None
        if self.hash in resource_dict:
            return resource_dict[self.hash]
        elif hasattr(self, 'path'):
            game_root = game_root_ps4 if is_ps4 else game_root_pc
            full_path = os.path.join(game_root, self.path) + '.core'
            read_objects(full_path, resource_dict)
            if self.hash in resource_dict:
                return resource_dict[self.hash]
        raise Exception('Resource not in list: {}'.format(self.__str__()))

    def __str__(self):
        ret = 'Type {} Ref: '.format(self.type)
        if hasattr(self, 'hash'):
            ret += binascii.hexlify(self.hash).decode('ASCII')
        if hasattr(self, 'path'):
            ret += ', ' + self.path
        return ret

    def __repr__(self):
        return self.__str__()


class UnknownResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        if self.uuid[:2] == b'\x00\x00':
            print('{} likely has starting short'.format(self.type))
            stream.seek(start_pos + 14)
            self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class AmmoResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class CharacterDescriptionComponentResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.character_name: Ref[LocalizedTextResource] = Ref(stream)
        self.unk_1 = Ref(stream)
        assert self.unk_1.type == 0
        self.character_type_class = Ref(stream)
        self.unk_2 = Ref(stream)
        assert self.unk_2.type == 0

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class CreditsColumn(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        name_len = struct.unpack('I', stream.read(4))[0]
        self.credits_name = read_utf16_chars(stream, name_len)
        self.style = Ref(stream)
        self.style_2 = Ref(stream)
        self.unk = Ref(stream)
        assert self.unk.type == 0

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class CreditsRow(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        column_count = struct.unpack('I', stream.read(4))[0]
        self.columns: List[Ref[CreditsColumn]] = [Ref(stream) for _ in range(column_count)]
        self.style = Ref(stream)
        self.unk_1, self.unk_2 = struct.unpack('bb', stream.read(2))

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class DamageAreaResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


class DataSourceCreditsResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        row_count = struct.unpack('I', stream.read(4))[0]
        self.rows: List[Ref[CreditsRow]] = [Ref(stream) for _ in range(row_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class EntityProjectileAmmoResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk1 = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        self.name = parse_hashed_string(stream)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class EntityResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk1 = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        self.name = parse_hashed_string(stream)
        stream.read(6)  # TODO
        Ref(stream)
        Ref(stream)
        Ref(stream)
        stream.read(15)
        Ref(stream)
        Ref(stream)
        ref_count = struct.unpack('I', stream.read(4))[0]
        self.ref_list: List[Ref] = [Ref(stream) for _ in range(ref_count)]
        self.unk6 = struct.unpack('f', stream.read(4))[0]
        self.unk7 = struct.unpack('b', stream.read(1))[0]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class ExplosionResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class FacialAnimationComponentResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.head_grp_multimesh = Ref(stream)
        self.skeleton = Ref(stream)
        self.bone_bounding_boxes = Ref(stream)
        self.neutral_anim = Ref(stream)
        self.unk_ints = struct.unpack('II', stream.read(8))[0]
        self.face_rig_data = Ref(stream)
        self.expressions = Ref(stream)
        # TODO
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class FocusScannedInfo(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.title: Ref[LocalizedTextResource] = Ref(stream)
        self.description_alternate: Ref[LocalizedTextResource] = Ref(stream)
        self.description: Ref[LocalizedTextResource] = Ref(stream)
        self.target_type = Ref(stream)
        category_count = struct.unpack('I', stream.read(4))[0]
        self.categories: List[Ref] = [Ref(stream) for _ in range(category_count)]
        self.scannable_body = Ref(stream)
        self.outlineSettings = Ref(stream)
        property_count = struct.unpack('I', stream.read(4))[0]
        self.properties: List[Ref] = [Ref(stream) for _ in range(property_count)]
        self.graph_condition = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class FocusTargetComponentResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.boolean_fact = Ref(stream)
        self.unk_short_1 = struct.unpack('h', stream.read(2))[0]
        self.unk_short_2 = struct.unpack('h', stream.read(2))[0]
        self.unk_int_1 = struct.unpack('I', stream.read(4))[0]
        assert self.unk_int_1 == 0
        self.unk_float = struct.unpack('f', stream.read(4))[0]
        self.unk_byte_1 = struct.unpack('b', stream.read(1))[0]
        assert self.unk_byte_1 == 0
        self.focus_scanned_info: Ref[FocusScannedInfo] = Ref(stream)
        unk_ref_count = struct.unpack('I', stream.read(4))[0]
        self.unk_ref_list = [Ref(stream) for _ in range(unk_ref_count)]
        self.unk_byte_2 = struct.unpack('b', stream.read(1))[0]
        self.focus_tracking_path_entity = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class HumanoidBodyVariant(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.model_part = Ref(stream)
        self.ability_pose_deformer = Ref(stream)
        unk_refs_1_count = struct.unpack('I', stream.read(4))[0]
        self.unk_refs_1: List[Ref] = [Ref(stream) for _ in range(unk_refs_1_count)]
        unk_refs_2_count = struct.unpack('I', stream.read(4))[0]
        self.unk_refs_2: List[Ref] = [Ref(stream) for _ in range(unk_refs_2_count)]
        unk_refs_3_count = struct.unpack('I', stream.read(4))[0]
        self.unk_refs_3: List[Ref] = [Ref(stream) for _ in range(unk_refs_3_count)]
        self.unk_ref_4 = Ref(stream)
        self.unk_int_5 = struct.unpack('I', stream.read(4))[0]
        self.unk_ref_6 = Ref(stream)
        self.unk_int_7 = struct.unpack('I', stream.read(4))[0]
        self.unk_float_8 = struct.unpack('f', stream.read(4))[0]
        unk_refs_9_count = struct.unpack('I', stream.read(4))[0]
        self.unk_refs_9: List[Ref] = [Ref(stream) for _ in range(unk_refs_9_count)]
        unk_strings_10_count = struct.unpack('I', stream.read(4))[0]
        self.unk_strings_10: List[str] = [parse_hashed_string(stream) for _ in range(unk_strings_10_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class HumanoidBodyVariantGroup(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        body_variants_count = struct.unpack('I', stream.read(4))[0]
        self.body_variants: List[Ref[HumanoidBodyVariant]] = [Ref(stream) for _ in range(body_variants_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class InventoryActionAbilityResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class InventoryAmmoEjectorResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        self.name = parse_hashed_string(stream)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class InventoryEntityResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        self.name = parse_hashed_string(stream)
        stream.read(7)  # TODO
        Ref(stream)
        stream.read(16)
        self.multiAction = Ref(stream)
        self.unk3 = Ref(stream)
        ref_count = struct.unpack('I', stream.read(4))[0]
        self.ref_list: List[Ref] = [Ref(stream) for _ in range(ref_count)]

        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class InventoryItemComponentResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.item_name: Ref[LocalizedTextResource] = Ref(stream)
        self.item_description: Ref[LocalizedTextResource] = Ref(stream)
        self.item_price_info = Ref(stream)
        self.unk = struct.unpack('I', stream.read(4))[0]
        self.item_icon = Ref(stream)
        self.item_icon_2 = Ref(stream)
        self.broken_ref = Ref(stream)
        self.unk_ref = Ref(stream)
        self.unk_ref2 = Ref(stream)
        self.unk_ref3 = Ref(stream)
        ref_count = struct.unpack('I', stream.read(4))[0]
        self.ref_list: List[Ref] = [Ref(stream) for _ in range(ref_count)]
        self.unk_short = struct.unpack('H', stream.read(2))[0]
        ref_count_2 = struct.unpack('I', stream.read(4))[0]
        self.ref_list_2: List[Ref] = [Ref(stream) for _ in range(ref_count_2)]
        stream.read(5)  # TODO
        self.soundbank = Ref(stream)
        self.unk_ref3 = Ref(stream)
        stream.read(2)  # TODO


class InventoryLootPackageComponentResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_ref = Ref(stream)
        assert(self.unk_ref.type == 0), "unk_ref populated"
        ref_count = struct.unpack('I', stream.read(4))[0]
        self.loot_slot: List[Ref[LootSlot]] = [Ref(stream) for _ in range(ref_count)]
        self.inventory_item_component: Ref[InventoryItemComponentResource] = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class LocalizedAnimationResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.unk_1 = struct.unpack('I', stream.read(4))[0]
        self.unk_2 = struct.unpack('I', stream.read(4))[0]
        self.unk_3 = Ref(stream)


class LocalizedSimpleSoundResource(Resource):
    class SoundInfo:
        def __init__(self, stream: BinaryIO):
            self.size_1 = struct.unpack('I', stream.read(4))[0]
            self.sample_count = struct.unpack('I', stream.read(4))[0]
            self.unk_3 = struct.unpack('I', stream.read(4))[0]
            assert(self.unk_3 == 0)
            self.start = struct.unpack('I', stream.read(4))[0]
            self.unk_5 = struct.unpack('I', stream.read(4))[0]
            assert (self.unk_5 == 0)
            self.size_2 = struct.unpack('I', stream.read(4))[0]
            self.unk_7 = struct.unpack('I', stream.read(4))[0]
            assert (self.unk_7 == 0)
            assert (self.size_1 == self.size_2), "size 1 and 2 don't match"

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_floats_1: List[float] = [struct.unpack('f', stream.read(4))[0] for _ in range(17)]
        self.unk_bytes_2 = stream.read(17)
        self.unk_floats_3: List[float] = [struct.unpack('f', stream.read(4))[0] for _ in range(9)]
        self.unk_bytes_4 = stream.read(3)
        self.state_relative_mix = Ref(stream)
        self.sound_preset = Ref(stream)
        filename_len = struct.unpack('I', stream.read(4))[0]
        self.sound_filename = stream.read(filename_len).decode('UTF8')
        self.language_flags = struct.unpack('H', stream.read(2))[0]
        assert (self.language_flags <= 0xFFF), "unrecognized language flag"
        self.unk_bytes_5 = stream.read(6)
        # 9: at9
        # b: mp3
        # d: at9?
        # f: at9
        assert(self.unk_bytes_5[1] in [0x09, 0x0b, 0x0d, 0x0f]), "unrecognized sound type"
        self.sample_rate = struct.unpack('I', stream.read(4))[0]
        self.unk_short_6 = struct.unpack('H', stream.read(2))[0]
        assert(self.unk_short_6 == 16), "unk_short_6 not 16"
        self.bit_rate = struct.unpack('I', stream.read(4))[0]
        self.unk_short_7 = struct.unpack('H', stream.read(2))[0]
        self.unk_short_8 = struct.unpack('H', stream.read(2))[0]
        self.sound_info: List[LocalizedSimpleSoundResource.SoundInfo] = list()
        for i in range(12):
            if self.language_flags & (1 << i) != 0:
                self.sound_info.append(LocalizedSimpleSoundResource.SoundInfo(stream))

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class LocalizedTextResource(Resource):
    @staticmethod
    def read_fixed_string(stream: BinaryIO):
        size = struct.unpack('H', stream.read(2))[0]
        return stream.read(size).decode('UTF8')

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.english = LocalizedTextResource.read_fixed_string(stream)
        self.french = LocalizedTextResource.read_fixed_string(stream)
        self.spanish = LocalizedTextResource.read_fixed_string(stream)
        self.german = LocalizedTextResource.read_fixed_string(stream)
        self.italian = LocalizedTextResource.read_fixed_string(stream)
        self.dutch = LocalizedTextResource.read_fixed_string(stream)
        self.portuguese = LocalizedTextResource.read_fixed_string(stream)
        self.traditional_chinese = LocalizedTextResource.read_fixed_string(stream)
        self.korean = LocalizedTextResource.read_fixed_string(stream)
        self.russian = LocalizedTextResource.read_fixed_string(stream)
        self.polish = LocalizedTextResource.read_fixed_string(stream)
        self.danish = LocalizedTextResource.read_fixed_string(stream)
        self.finnish = LocalizedTextResource.read_fixed_string(stream)
        self.norwegian = LocalizedTextResource.read_fixed_string(stream)
        self.swedish = LocalizedTextResource.read_fixed_string(stream)
        self.japanese = LocalizedTextResource.read_fixed_string(stream)
        self.latin_american_spanish = LocalizedTextResource.read_fixed_string(stream)
        self.brazilian_portuguese = LocalizedTextResource.read_fixed_string(stream)
        self.turkish = LocalizedTextResource.read_fixed_string(stream)
        self.arabic = LocalizedTextResource.read_fixed_string(stream)
        self.simplified_chinese = LocalizedTextResource.read_fixed_string(stream)

    def __str__(self):
        return self.english.strip()

    def __repr__(self):
        return self.english.__repr__()


class LootData(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.probability: float = struct.unpack('f', stream.read(4))[0]
        self.unkRef = Ref(stream)  # Never seems to be valid(?)
        ref_count = struct.unpack('I', stream.read(4))[0]
        self.loot_item: List[Ref[LootItem]] = [Ref(stream) for _ in range(ref_count)]
        self.quantity: int = struct.unpack('I', stream.read(4))[0]
        self.unk3: int = struct.unpack('b', stream.read(1))[0]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class LootItem(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk: float = struct.unpack('f', stream.read(4))[0]
        self.unk2 = Ref(stream)
        self.inventoryEntity = Ref(stream)

        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class LootSlot(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        ref_count = struct.unpack('I', stream.read(4))[0]
        self.loot_data: List[Ref[LootData]] = [Ref(stream) for _ in range(ref_count)]
        self.loot_slot_settings: Ref = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class ObjectCollection(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        objects_count = struct.unpack('I', stream.read(4))[0]
        self.objects: List[Ref[CreditsRow]] = [Ref(stream) for _ in range(objects_count)]


# TODO: Unfinished
class SentenceResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_int = struct.unpack('I', stream.read(4))[0]
        self.unk_byte_1 = struct.unpack('b', stream.read(1))[0]
        self.unk_byte_2 = struct.unpack('b', stream.read(1))[0]
        self.sound: Ref[LocalizedSimpleSoundResource] = Ref(stream)
        self.animation: Ref = Ref(stream)
        self.text: Ref[LocalizedTextResource] = Ref(stream)
        self.voice: Ref[VoiceResource] = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class SentenceGroupResource(Resource):
    class ESentenceGroupType(IntEnum):
        Normal = 0,
        OneOfRandom = 1,
        OneOfInOrder = 2

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        sentence_type = struct.unpack('I', stream.read(4))[0]
        self.sentence_type = SentenceGroupResource.ESentenceGroupType(sentence_type)
        sentences_count = struct.unpack('I', stream.read(4))[0]
        self.sentences: List[Ref[SentenceResource]] = [Ref(stream) for _ in range(sentences_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class SpawnSetup(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.graph_condition = Ref(stream)
        self.impostor = Ref(stream)
        self.humanoid = Ref(stream)
        self.graph_program = Ref(stream)
        self.faction = Ref(stream)
        unk_refs_1_count = struct.unpack('I', stream.read(4))[0]
        self.unk_refs_1: List[Ref] = [Ref(stream) for _ in range(unk_refs_1_count)]
        unk_refs_2_count = struct.unpack('I', stream.read(4))[0]
        self.unk_refs_2: List[Ref] = [Ref(stream) for _ in range(unk_refs_2_count)]
        self.unk_ints = struct.unpack('iii', stream.read(12))
        self.unk_byte = struct.unpack('b', stream.read(1))
        unk_refs_3_count = struct.unpack('I', stream.read(4))[0]
        self.unk_refs_3: List[Ref] = [Ref(stream) for _ in range(unk_refs_3_count)]
        self.inventory_collection = Ref(stream)
        self.combat_behavior = Ref(stream)
        self.humanoid_body_variant: [Ref[HumanoidBodyVariant], Ref[HumanoidBodyVariantGroup]] = Ref(stream)
        self.combat_properties = Ref(stream)
        self.combat_properties_facts = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class SpawnSetupGroup(Resource):
    class UnkStruct:
        def __init__(self, stream: BinaryIO):
            self.unk_float = struct.unpack('f', stream.read(4))[0]
            self.unk_ref: [Ref[SpawnSetup], Ref[SpawnSetupGroup]] = Ref(stream)

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_boolean_fact = Ref(stream)
        self.unk2 = Ref(stream)
        assert self.unk2.type == 0
        unk_struct_count = struct.unpack('I', stream.read(4))[0]
        self.unk_structs = [SpawnSetupGroup.UnkStruct(stream) for _ in range(unk_struct_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class ThrowableResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


class VoiceComponentResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        voice_signals_count = struct.unpack('I', stream.read(4))[0]
        self.voice_signals: List[Ref[VoiceSignalsResource]] = [Ref(stream) for _ in range(voice_signals_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class VoiceResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_1 = stream.read(4)
        self.unk_2 = struct.unpack('b', stream.read(1))[0]
        self.text: Ref[LocalizedTextResource] = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class VoiceSignalsResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.voice: Ref[VoiceResource] = Ref(stream)
        sentences_count = struct.unpack('I', stream.read(4))[0]
        self.sentences: List[Ref[SentenceResource]] = [Ref(stream) for _ in range(sentences_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: There has to be a better way of splitting this out
script_dir = os.path.dirname(__file__)
ps4_type_map = eval(open(os.path.join(script_dir, r'ps4_type_map.txt'), 'r').read())
pc_type_map = eval(open(os.path.join(script_dir, r'pc_type_map.txt'), 'r').read())


def read_objects(in_file_name: str, out_dict: Dict[bytes, Resource], use_buffering=False):
    global is_ps4
    is_ps4 = 'packed_pink' in in_file_name
    type_map = ps4_type_map if is_ps4 else pc_type_map

    with open(in_file_name, 'rb') as in_file:
        while True:
            start_pos = in_file.tell()
            if not in_file.read(1):
                break
            in_file.seek(start_pos)
            type_hash, size = struct.unpack('QI', in_file.read(12))
            in_file.seek(start_pos)
            if use_buffering:
                stream = io.BytesIO(in_file.read(12 + size))
            else:
                stream = in_file
            # check type map to see if we have a dedicated constructor
            littleendian_type = '{0:X}'.format(type_hash)
            type_info = ["Unknown"]
            if littleendian_type in type_map:
                type_info = type_map['{0:X}'.format(type_hash)]
            if len(type_info) > 1:
                parse_start_pos = stream.tell()

                try:
                    specific_res = type_info[1](stream)
                    out_dict[specific_res.uuid] = specific_res
                except:
                    stream.seek(parse_start_pos)
                    unknown_res = UnknownResource(stream)
                    raise Exception("{} {} in {} failed to parse"
                          .format(type_info[0], binascii.hexlify(unknown_res.uuid).decode('ASCII'),
                                  in_file_name))

                parse_end_pos = stream.tell()
                read_count = (parse_end_pos - parse_start_pos)
                if size + 12 != read_count:
                    print("{} {} in {} didn't match size, expected {}, read {}"
                          .format(specific_res.type, binascii.hexlify(specific_res.uuid).decode('ASCII'),
                                  in_file_name, size + 12, read_count))
            else:
                unknown_res = UnknownResource(stream)
                out_dict[unknown_res.uuid] = unknown_res


def parse_hashed_string(stream: BinaryIO):
    size = struct.unpack('I', stream.read(4))[0]
    if size > 0:
        string_hash = stream.read(4)
    return stream.read(size).decode('ASCII')


def read_utf16_chars(stream: BinaryIO, length):
    # Read one byte at a time
    binary_chunks = iter(partial(stream.read, 1), "")
    # Convert bytes into unicode code points
    decoder = iterdecode(binary_chunks, 'utf_16_le')
    return str().join(islice(decoder, length))
