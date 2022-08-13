import binascii
import struct
import os
import io
from codecs import iterdecode
from enum import IntEnum
from functools import partial
from itertools import islice

from typing import Dict, BinaryIO, TypeVar, Generic, List, Optional, Any

script_dir = os.path.dirname(__file__)
ps4_path_file = os.path.join(script_dir, r'hzd_ps4_root_path.txt')
pc_path_file = os.path.join(script_dir, r'hzd_root_path.txt')
game_root_ps4 = open(ps4_path_file, 'r').read().strip('" \t\r\n') if os.path.isfile(ps4_path_file) else ''
game_root_pc = open(pc_path_file, 'r').read().strip('" \t\r\n') if os.path.isfile(pc_path_file) else ''
is_ps4 = False
T = TypeVar('T')


class ETextLanguages(IntEnum):
    English = 0,
    French = 1,
    Spanish = 2,
    German = 3,
    Italian = 4,
    Dutch = 5,
    Portuguese = 6,
    TraditionalChinese = 7,
    Korean = 8,
    Russian = 9,
    Polish = 10,
    Danish = 11,
    Finnish = 12,
    Norwegian = 13,
    Swedish = 14,
    Japanese = 15,
    LatinAmericanSpanish = 16,
    BrazilianPortuguese = 17,
    Turkish = 18,
    Arabic = 19,
    SimplifiedChinese = 20


class EAudioLanguages(IntEnum):
    English = 0,
    French = 1,
    Spanish = 2,
    German = 3,
    Italian = 4,
    Portugese = 5,
    Russian = 6,
    Polish = 7,
    Japanese = 8,
    LatAmSp = 9,  # Latin-American Spanish
    LatAmPor = 10,  # Brazilian Portuguese
    Arabic = 11


class ImageStruct:
    class ImageFormat(IntEnum):
        INVALID = 0x4C,
        RGBA_5551 = 0x0,
        RGBA_5551_REV = 0x1,
        RGBA_4444 = 0x2,
        RGBA_4444_REV = 0x3,
        RGB_888_32 = 0x4,
        RGB_888_32_REV = 0x5,
        RGB_888 = 0x6,
        RGB_888_REV = 0x7,
        RGB_565 = 0x8,
        RGB_565_REV = 0x9,
        RGB_555 = 0xA,
        RGB_555_REV = 0xB,
        RGBA_8888 = 0xC,
        RGBA_8888_REV = 0xD,
        RGBE_REV = 0xE,
        RGBA_FLOAT_32 = 0xF,
        RGB_FLOAT_32 = 0x10,
        RG_FLOAT_32 = 0x11,
        R_FLOAT_32 = 0x12,
        RGBA_FLOAT_16 = 0x13,
        RGB_FLOAT_16 = 0x14,
        RG_FLOAT_16 = 0x15,
        R_FLOAT_16 = 0x16,
        RGBA_UNORM_32 = 0x17,
        RG_UNORM_32 = 0x18,
        R_UNORM_32 = 0x19,
        RGBA_UNORM_16 = 0x1A,
        RG_UNORM_16 = 0x1B,
        R_UNORM_16 = 0x1C,  # Old: INTENSITY_16
        RGBA_UNORM_8 = 0x1D,
        RG_UNORM_8 = 0x1E,
        R_UNORM_8 = 0x1F,  # Old: INTENSITY_8
        RGBA_NORM_32 = 0x20,
        RG_NORM_32 = 0x21,
        R_NORM_32 = 0x22,
        RGBA_NORM_16 = 0x23,
        RG_NORM_16 = 0x24,
        R_NORM_16 = 0x25,
        RGBA_NORM_8 = 0x26,
        RG_NORM_8 = 0x27,
        R_NORM_8 = 0x28,
        RGBA_UINT_32 = 0x29,
        RG_UINT_32 = 0x2A,
        R_UINT_32 = 0x2B,
        RGBA_UINT_16 = 0x2C,
        RG_UINT_16 = 0x2D,
        R_UINT_16 = 0x2E,
        RGBA_UINT_8 = 0x2F,
        RG_UINT_8 = 0x30,
        R_UINT_8 = 0x31,
        RGBA_INT_32 = 0x32,
        RG_INT_32 = 0x33,
        R_INT_32 = 0x34,
        RGBA_INT_16 = 0x35,
        RG_INT_16 = 0x36,
        R_INT_16 = 0x37,
        RGBA_INT_8 = 0x38,
        RG_INT_8 = 0x39,
        R_INT_8 = 0x3A,
        RGB_FLOAT_11_11_10 = 0x3B,
        RGBA_UNORM_10_10_10_2 = 0x3C,
        RGB_UNORM_11_11_10 = 0x3D,
        DEPTH_FLOAT_32_STENCIL_8 = 0x3E,
        DEPTH_FLOAT_32_STENCIL_0 = 0x3F,
        DEPTH_24_STENCIL_8 = 0x40,
        DEPTH_16_STENCIL_0 = 0x41,
        BC1 = 0x42,  # Old: S3TC1
        BC2 = 0x43,  # Old: S3TC3
        BC3 = 0x44,  # Old: S3TC5
        BC4U = 0x45,
        BC4S = 0x46,
        BC5U = 0x47,
        BC5S = 0x48,
        BC6U = 0x49,
        BC6S = 0x4A,
        BC7 = 0x4B

    def __init__(self, stream: BinaryIO):
        self.unk_short1 = struct.unpack('<H', stream.read(2))[0]
        width = struct.unpack('<H', stream.read(2))[0]
        self.width = width & 0x3FFF
        self.width_crop = width >> 14
        height = struct.unpack('<H', stream.read(2))[0]
        self.height = height & 0x3FFF
        self.height_crop = height >> 14
        self.unk_short2 = struct.unpack('<H', stream.read(2))[0]
        self.unk_byte1 = struct.unpack('<B', stream.read(1))[0]
        self.image_format: ImageStruct.ImageFormat = self.ImageFormat(struct.unpack('<B', stream.read(1))[0])
        self.unk_byte2 = struct.unpack('<B', stream.read(1))[0]
        self.unk_byte3 = struct.unpack('<B', stream.read(1))[0]
        self.magic = stream.read(4)
        #assert self.magic == b'\x00\xA9\xFF\x00'
        self.maybe_hash = stream.read(16)
        self.image_chunk_size = struct.unpack('<I', stream.read(4))[0]
        # TODO: Assert here?
        if is_ps4:
            self.size_with_stream = struct.unpack('<I', stream.read(4))[0]
            self.size_without_stream = struct.unpack('<I', stream.read(4))[0]
            if self.size_with_stream != self.size_without_stream:
                self.size_of_stream = struct.unpack('<I', stream.read(4))[0]
                assert self.size_with_stream == self.size_without_stream + self.size_of_stream, \
                       "Stream size doesn't add up"
                self.mipmaps_in_stream = struct.unpack('<I', stream.read(4))[0]
                self.image_contents = stream.read(self.size_without_stream)
                cache_len = struct.unpack('<I', stream.read(4))[0]
                self.cache_string = stream.read(cache_len).decode('ASCII')
                self.stream_start = struct.unpack('<Q', stream.read(8))[0]
                self.stream_end = struct.unpack('<Q', stream.read(8))[0]
            else:
                stream.read(self.image_chunk_size - (self.size_without_stream + 8))  # padding
                self.image_contents = stream.read(self.size_without_stream)
        else:
            self.size_without_stream = struct.unpack('<I', stream.read(4))[0]
            self.size_of_stream = struct.unpack('<I', stream.read(4))[0]
            if self.size_of_stream > 0:
                self.mipmaps_in_stream = struct.unpack('<I', stream.read(4))[0]
                cache_len = struct.unpack('<I', stream.read(4))[0]
                self.cache_string = stream.read(cache_len).decode('ASCII')
                self.stream_start = struct.unpack('<Q', stream.read(8))[0]
                self.size_of_stream2 = struct.unpack('<Q', stream.read(8))[0]
                assert self.size_of_stream == self.size_of_stream2, "Stream sizes don't match"
            else:
                stream.read(self.image_chunk_size - (self.size_without_stream + 8))  # padding
            self.image_contents = stream.read(self.size_without_stream)


class Resource:
    def __init__(self, stream: BinaryIO):
        self.type_hash = struct.unpack('<Q', stream.read(8))[0]
        little_endian_type = '{0:X}'.format(self.type_hash)
        type_map = ps4_type_map if is_ps4 else pc_type_map
        if little_endian_type in type_map:
            self.type = type_map[little_endian_type][0]
        else:
            self.type = 'Unknown Type'
        self.size = struct.unpack('<I', stream.read(4))[0]
        self.uuid = stream.read(16)

    def __str__(self):
        return '{}: {}'.format(self.type, binascii.hexlify(self.uuid).decode('ASCII'))

    def __repr__(self):
        return self.__str__()


class Ref(Generic[T]):
    def __init__(self, stream: BinaryIO):
        self.type: int = struct.unpack('<B', stream.read(1))[0]
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
        self.unk = struct.unpack('<h', stream.read(2))[0]
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


# TODO: Unfinished
class CollisionTrigger(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<I', stream.read(4))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


class CreditsColumn(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        name_len = struct.unpack('<I', stream.read(4))[0]
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
        column_count = struct.unpack('<I', stream.read(4))[0]
        self.columns: List[Ref[CreditsColumn]] = [Ref(stream) for _ in range(column_count)]
        self.style = Ref(stream)
        self.unk_1, self.unk_2 = struct.unpack('<bb', stream.read(2))

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class DamageAreaResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


class DataSourceCreditsResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        row_count = struct.unpack('<I', stream.read(4))[0]
        self.rows: List[Ref[CreditsRow]] = [Ref(stream) for _ in range(row_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class EntityProjectileAmmoResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk1 = struct.unpack('<h', stream.read(2))[0]
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
        self.unk1 = struct.unpack('<h', stream.read(2))[0]
        self.uuid = stream.read(16)
        self.name = parse_hashed_string(stream)
        stream.read(6)  # TODO
        Ref(stream)
        Ref(stream)
        Ref(stream)
        stream.read(15)
        Ref(stream)
        Ref(stream)
        ref_count = struct.unpack('<I', stream.read(4))[0]
        self.ref_list: List[Ref] = [Ref(stream) for _ in range(ref_count)]
        self.unk6 = struct.unpack('<f', stream.read(4))[0]
        self.unk7 = struct.unpack('<b', stream.read(1))[0]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class ExplosionResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<h', stream.read(2))[0]
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
        self.unk_ints = struct.unpack('<II', stream.read(8))[0]
        self.face_rig_data = Ref(stream)
        self.expressions = Ref(stream)
        # TODO
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class FactCollisionTrigger(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<I', stream.read(4))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class FocusScannedInfo(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.title: Ref[LocalizedTextResource] = Ref(stream)
        self.description_alternate: Ref[LocalizedTextResource] = Ref(stream)
        self.description: Ref[LocalizedTextResource] = Ref(stream)
        self.target_type = Ref(stream)
        category_count = struct.unpack('<I', stream.read(4))[0]
        self.categories: List[Ref] = [Ref(stream) for _ in range(category_count)]
        self.scannable_body = Ref(stream)
        self.outlineSettings = Ref(stream)
        property_count = struct.unpack('<I', stream.read(4))[0]
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
        self.unk_short_1 = struct.unpack('<h', stream.read(2))[0]
        self.unk_short_2 = struct.unpack('<h', stream.read(2))[0]
        self.unk_int_1 = struct.unpack('<I', stream.read(4))[0]
        assert self.unk_int_1 == 0
        self.unk_float = struct.unpack('<f', stream.read(4))[0]
        self.unk_byte_1 = struct.unpack('<b', stream.read(1))[0]
        assert self.unk_byte_1 == 0
        self.focus_scanned_info: Ref[FocusScannedInfo] = Ref(stream)
        unk_ref_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_ref_list = [Ref(stream) for _ in range(unk_ref_count)]
        self.unk_byte_2 = struct.unpack('<b', stream.read(1))[0]
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
        unk_refs_1_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_refs_1: List[Ref] = [Ref(stream) for _ in range(unk_refs_1_count)]
        unk_refs_2_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_refs_2: List[Ref] = [Ref(stream) for _ in range(unk_refs_2_count)]
        unk_refs_3_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_refs_3: List[Ref] = [Ref(stream) for _ in range(unk_refs_3_count)]
        self.unk_ref_4 = Ref(stream)
        self.unk_int_5 = struct.unpack('<I', stream.read(4))[0]
        self.unk_ref_6 = Ref(stream)
        self.unk_int_7 = struct.unpack('<I', stream.read(4))[0]
        self.unk_float_8 = struct.unpack('<f', stream.read(4))[0]
        unk_refs_9_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_refs_9: List[Ref] = [Ref(stream) for _ in range(unk_refs_9_count)]
        unk_strings_10_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_strings_10: List[str] = [parse_hashed_string(stream) for _ in range(unk_strings_10_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class HumanoidBodyVariantGroup(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        body_variants_count = struct.unpack('<I', stream.read(4))[0]
        self.body_variants: List[Ref[HumanoidBodyVariant]] = [Ref(stream) for _ in range(body_variants_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class InventoryActionAbilityResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class InventoryAmmoEjectorResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<h', stream.read(2))[0]
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
        self.unk = struct.unpack('<h', stream.read(2))[0]
        self.uuid = stream.read(16)
        self.name = parse_hashed_string(stream)
        stream.read(7)  # TODO
        Ref(stream)
        stream.read(16)
        self.multiAction = Ref(stream)
        self.unk3 = Ref(stream)
        ref_count = struct.unpack('<I', stream.read(4))[0]
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
        self.unk = struct.unpack('<I', stream.read(4))[0]
        self.item_icon = Ref(stream)
        self.item_icon_2 = Ref(stream)
        self.broken_ref = Ref(stream)
        self.unk_ref = Ref(stream)
        self.unk_ref2 = Ref(stream)
        self.unk_ref3 = Ref(stream)
        ref_count = struct.unpack('<I', stream.read(4))[0]
        self.ref_list: List[Ref] = [Ref(stream) for _ in range(ref_count)]
        self.unk_short = struct.unpack('<H', stream.read(2))[0]
        ref_count_2 = struct.unpack('<I', stream.read(4))[0]
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
        ref_count = struct.unpack('<I', stream.read(4))[0]
        self.loot_slot: List[Ref[LootSlot]] = [Ref(stream) for _ in range(ref_count)]
        self.inventory_item_component: Ref[InventoryItemComponentResource] = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class LocalizedAnimationResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.unk_1 = struct.unpack('<I', stream.read(4))[0]
        self.unk_2 = struct.unpack('<I', stream.read(4))[0]
        self.unk_3 = Ref(stream)


class LocalizedSimpleSoundResource(Resource):
    class SoundInfo:
        def __init__(self, stream: BinaryIO):
            self.size_1 = struct.unpack('<I', stream.read(4))[0]
            self.sample_count = struct.unpack('<I', stream.read(4))[0]
            self.unk_3 = struct.unpack('<I', stream.read(4))[0]
            assert(self.unk_3 == 0)
            self.start = struct.unpack('<I', stream.read(4))[0]
            self.unk_5 = struct.unpack('<I', stream.read(4))[0]
            assert (self.unk_5 == 0)
            self.size_2 = struct.unpack('<I', stream.read(4))[0]
            self.unk_7 = struct.unpack('<I', stream.read(4))[0]
            assert (self.unk_7 == 0)
            assert (self.size_1 == self.size_2), "size 1 and 2 don't match"

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_floats_1: List[float] = [struct.unpack('<f', stream.read(4))[0] for _ in range(17)]
        self.unk_bytes_2 = stream.read(17)
        self.unk_floats_3: List[float] = [struct.unpack('<f', stream.read(4))[0] for _ in range(9)]
        self.unk_bytes_4 = stream.read(3)
        self.state_relative_mix = Ref(stream)
        self.sound_preset = Ref(stream)
        filename_len = struct.unpack('<I', stream.read(4))[0]
        self.sound_filename = stream.read(filename_len).decode('UTF8')
        self.language_flags = struct.unpack('<H', stream.read(2))[0]
        assert (self.language_flags <= 0xFFF), "unrecognized language flag"
        self.unk_byte_5 = stream.read(1)
        self.audio_type = struct.unpack('<b', stream.read(1))[0]
        # 9: at9
        # b: mp3
        # d: at9, TODO: Figure out what's different from 9
        # f: aac, ps4-only
        assert(self.audio_type in [0x09, 0x0b, 0x0d, 0x0f]), f"unrecognized sound type {self.audio_type}"
        self.unk_bytes_6 = stream.read(4)
        self.sample_rate = struct.unpack('<I', stream.read(4))[0]
        self.bits_per_sample = struct.unpack('<H', stream.read(2))[0]
        self.bit_rate = struct.unpack('<I', stream.read(4))[0]
        self.unk_short_8 = struct.unpack('<H', stream.read(2))[0]
        self.unk_short_9 = struct.unpack('<H', stream.read(2))[0]
        self.sound_info: List[Optional[LocalizedSimpleSoundResource.SoundInfo]] = list()
        for i in range(12):
            if self.language_flags & (1 << i) != 0:
                self.sound_info.append(LocalizedSimpleSoundResource.SoundInfo(stream))
            else:
                self.sound_info.append(None)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class LocalizedTextResource(Resource):
    @staticmethod
    def read_fixed_string(stream: BinaryIO):
        size = struct.unpack('<H', stream.read(2))[0]
        return stream.read(size).decode('UTF8')

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.language = [LocalizedTextResource.read_fixed_string(stream) for _ in ETextLanguages]

    def __str__(self):
        return self.language[ETextLanguages.English].strip()

    def __repr__(self):
        return self.language[ETextLanguages.English].__repr__()


class LootData(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.probability: float = struct.unpack('<f', stream.read(4))[0]
        self.unkRef = Ref(stream)  # Never seems to be valid(?)
        ref_count = struct.unpack('<I', stream.read(4))[0]
        self.loot_item: List[Ref[LootItem]] = [Ref(stream) for _ in range(ref_count)]
        self.quantity: int = struct.unpack('<I', stream.read(4))[0]
        self.unk3: int = struct.unpack('<b', stream.read(1))[0]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class LootItem(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk: float = struct.unpack('<f', stream.read(4))[0]
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
        ref_count = struct.unpack('<I', stream.read(4))[0]
        self.loot_data: List[Ref[LootData]] = [Ref(stream) for _ in range(ref_count)]
        self.loot_slot_settings: Ref = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class ObjectCollection(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        objects_count = struct.unpack('<I', stream.read(4))[0]
        self.objects: List[Ref[CreditsRow]] = [Ref(stream) for _ in range(objects_count)]


# TODO: Unfinished
class OutOfBoundsNavMeshArea(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        stream.read(60)  # TODO: don't skip this
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class PhysicsCollisionResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<I', stream.read(4))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


# TODO: Unfinished
class PrefetchList(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        paths_count = struct.unpack('<I', stream.read(4))[0]
        self.paths: List[HashedString] = [parse_hashed_string(stream, True) for _ in range(paths_count)]
        sizes_count = struct.unpack('<I', stream.read(4))[0]
        assert (paths_count == sizes_count), "differing number of paths and sizes"
        self.sizes = [struct.unpack('<I', stream.read(4))[0] for _ in range(sizes_count)]
        indices_count = struct.unpack('<I', stream.read(4))[0]
        self.indices = [struct.unpack('<I', stream.read(4))[0] for _ in range(indices_count)]


# TODO: Unfinished
class SentenceResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_int = struct.unpack('<I', stream.read(4))[0]
        self.unk_byte_1 = struct.unpack('<b', stream.read(1))[0]
        self.unk_byte_2 = struct.unpack('<b', stream.read(1))[0]
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
        sentence_type = struct.unpack('<I', stream.read(4))[0]
        self.sentence_type = SentenceGroupResource.ESentenceGroupType(sentence_type)
        sentences_count = struct.unpack('<I', stream.read(4))[0]
        self.sentences: List[Ref[SentenceResource]] = [Ref(stream) for _ in range(sentences_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class SkeletonAnimationResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.data = stream.read(self.size - 16)


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
        unk_refs_1_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_refs_1: List[Ref] = [Ref(stream) for _ in range(unk_refs_1_count)]
        unk_refs_2_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_refs_2: List[Ref] = [Ref(stream) for _ in range(unk_refs_2_count)]
        self.unk_ints = struct.unpack('<iii', stream.read(12))
        self.unk_byte = struct.unpack('<b', stream.read(1))
        unk_refs_3_count = struct.unpack('<I', stream.read(4))[0]
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
            self.unk_float = struct.unpack('<f', stream.read(4))[0]
            self.unk_ref: [Ref[SpawnSetup], Ref[SpawnSetupGroup]] = Ref(stream)

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_boolean_fact = Ref(stream)
        self.unk2 = Ref(stream)
        assert self.unk2.type == 0
        unk_struct_count = struct.unpack('<I', stream.read(4))[0]
        self.unk_structs = [SpawnSetupGroup.UnkStruct(stream) for _ in range(unk_struct_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class Texture(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        if self.size - (stream.tell() - start_pos) > 0:
            self.image_data = ImageStruct(stream)

    def __str__(self):
        streamed = hasattr(self.image_data, "size_of_stream") and self.image_data.size_of_stream > 0
        return f'{self.type}: {self.name}, {self.image_data.width}x{self.image_data.height}, ' + \
               f'{self.image_data.image_format.name}, {"streamed " if streamed else ""}' + \
               f'@{hex(self.image_data.stream_start) if streamed else "internal"}'


class TextureSet(Resource):
    class ETextureSetType(IntEnum):
        Invalid = 0x0,
        Color = 0x1,
        Alpha = 0x2,
        Normal = 0x3,
        Reflectance = 0x4,
        AO = 0x5,
        Roughness = 0x6,
        Height = 0x7,
        Mask = 0x8,
        Mask_Alpha = 0x9,
        Incandescence = 0xA,
        Translucency_Diffusion = 0xB,
        Translucency_Amount = 0xC,
        Misc_01 = 0xD,
        Count = 0xE

    class TextureDetails:
        class ChannelDetails:
            def __init__(self, stream: BinaryIO):
                channel_details = struct.unpack('<B', stream.read(1))[0]
                self.setType: TextureSet.ETextureSetType = TextureSet.ETextureSetType(channel_details & 0x0F)
                self.unk = channel_details >> 4

        def __init__(self, stream: BinaryIO):
            self.unk_int1 = struct.unpack('<I', stream.read(4))[0]
            self.unk_int2 = struct.unpack('<I', stream.read(4))[0]
            self.unk_byte = struct.unpack('<b', stream.read(1))
            self.channel_details: List[TextureSet.TextureDetails.ChannelDetails] = \
                [self.ChannelDetails(stream) for _ in range(4)]
            self.unk_int3 = struct.unpack('<I', stream.read(4))[0]
            self.texture: Ref[Texture] = Ref(stream)

    class SourceDetails:
        def __init__(self, stream: BinaryIO):
            set_type_int = struct.unpack('<I', stream.read(4))[0]
            self.set_type: TextureSet.ETextureSetType = TextureSet.ETextureSetType(set_type_int)
            self.source_filename = parse_hashed_string(stream)
            self.unk_byte1 = struct.unpack('<b', stream.read(1))
            self.unk_byte2 = struct.unpack('<b', stream.read(1))
            self.unk_int1 = struct.unpack('<I', stream.read(4))[0]
            self.unk_int2 = struct.unpack('<I', stream.read(4))[0]
            self.unk_int3 = struct.unpack('<I', stream.read(4))[0]
            self.width = struct.unpack('<I', stream.read(4))[0]
            self.height = struct.unpack('<I', stream.read(4))[0]
            self.unk_float1 = struct.unpack('<f', stream.read(4))[0]
            self.unk_float2 = struct.unpack('<f', stream.read(4))[0]
            self.unk_float3 = struct.unpack('<f', stream.read(4))[0]
            self.unk_float4 = struct.unpack('<f', stream.read(4))[0]

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        texture_count = struct.unpack('<I', stream.read(4))[0]
        self.textures = [self.TextureDetails(stream) for _ in range(texture_count)]
        self.unk_int1 = struct.unpack('<I', stream.read(4))[0]
        assert self.unk_int1 == 0
        source_count = struct.unpack('<I', stream.read(4))[0]
        self.sources = [self.SourceDetails(stream) for _ in range(source_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class ThrowableResource(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.unk = struct.unpack('<h', stream.read(2))[0]
        self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


class UITexture(Resource):
    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        self.name_1 = parse_hashed_string(stream)
        self.name_2 = parse_hashed_string(stream)
        assert self.name_1 == self.name_2, f"UITexture names don't match: {self.name_1}, {self.name_2}"
        self.initial_width = struct.unpack('<I', stream.read(4))[0]
        self.initial_height = struct.unpack('<I', stream.read(4))[0]
        self.sizes = struct.unpack('<II', stream.read(8))
        self.image_data = ImageStruct(io.BytesIO(stream.read(self.sizes[0]))) if self.sizes[0] > 0 else None
        self.image_data_2 = ImageStruct(io.BytesIO(stream.read(self.sizes[1]))) if self.sizes[1] > 0 else None

    def __str__(self):
        streamed = hasattr(self.image_data_2, "size_of_stream") and self.image_data_2.size_of_stream > 0
        return f'{self.type}: {self.name_2}, {self.image_data_2.width}x{self.image_data_2.height}, ' + \
               f'{self.image_data_2.image_format.name}, {"streamed " if streamed else ""}' + \
               f'@{hex(self.image_data_2.stream_start) if streamed else "internal"}'


class VoiceComponentResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        voice_signals_count = struct.unpack('<I', stream.read(4))[0]
        self.voice_signals: List[Ref[VoiceSignalsResource]] = [Ref(stream) for _ in range(voice_signals_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: Unfinished
class VoiceResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.unk_1 = stream.read(4)
        self.unk_2 = struct.unpack('<b', stream.read(1))[0]
        self.text: Ref[LocalizedTextResource] = Ref(stream)

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class VoiceSignalsResource(Resource):
    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.name = parse_hashed_string(stream)
        self.voice: Ref[VoiceResource] = Ref(stream)
        sentences_count = struct.unpack('<I', stream.read(4))[0]
        self.sentences: List[Ref[SentenceResource]] = [Ref(stream) for _ in range(sentences_count)]

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class WaveResource(Resource):
    class EWaveDataEncoding(IntEnum):
        PCM = 0x0,
        PCM_FLOAT = 0x1,
        XWMA = 0x2,
        ATRAC9 = 0x3,
        MP3 = 0x4,
        ADPCM = 0x5,
        AAC = 0x6

    class EWaveDataEncodingQuality(IntEnum):
        Uncompressed__PCM_ = 0x0,
        Lossy_Lowest = 0x1,
        Lossy_Low = 0x2,
        Lossy_Medium = 0x3,
        Lossy_High = 0x4,
        Lossy_Highest = 0x5

    def __init__(self, stream: BinaryIO):
        start_pos = stream.tell()
        Resource.__init__(self, stream)
        stream.seek(start_pos + 12)
        self.encoding_quality = WaveResource.EWaveDataEncodingQuality(struct.unpack('<I', stream.read(4))[0])
        self.unk_bytes1 = struct.unpack('<bb', stream.read(2))
        self.uuid = stream.read(16)
        self.name = parse_hashed_string(stream)
        self.size_without_stream = struct.unpack('<I', stream.read(4))[0]
        if self.size_without_stream > 0:
            self.sound = stream.read(self.size_without_stream)
        self.size_with_stream = struct.unpack('<I', stream.read(4))[0]
        self.sample_rate = struct.unpack('<I', stream.read(4))[0]
        self.channels = struct.unpack('<b', stream.read(1))[0]
        self.encoding = WaveResource.EWaveDataEncoding(struct.unpack('<I', stream.read(4))[0])
        self.unk_short4 = struct.unpack('<H', stream.read(2))[0]
        self.bit_rate = struct.unpack('<I', stream.read(4))[0]
        self.unk_short5 = struct.unpack('<H', stream.read(2))[0]
        self.unk_short6 = struct.unpack('<H', stream.read(2))[0]
        self.unk_bytes7 = struct.unpack('<bbbbbb', stream.read(6))
        if self.size_with_stream != self.size_without_stream:
            cache_len = struct.unpack('<I', stream.read(4))[0]
            self.cache_string = stream.read(cache_len).decode('ASCII')
            self.unk_ints8 = struct.unpack('<IIII', stream.read(16))

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


# TODO: There has to be a better way of splitting this out
ps4_type_map = eval(open(os.path.join(script_dir, r'ps4_type_map.txt'), 'r').read())
pc_type_map = eval(open(os.path.join(script_dir, r'pc_type_map.txt'), 'r').read())


def read_objects(in_file_name: str, out_dict: Dict[bytes, Resource], use_buffering=False, ps4=False):
    global is_ps4
    is_ps4 = ps4
    type_map = ps4_type_map if is_ps4 else pc_type_map

    with open(in_file_name, 'rb') as in_file:
        try:
            return read_objects_from_stream(io.BytesIO(in_file.read()), type_map, out_dict, use_buffering)
        except Exception as e:
            raise Exception(f'Error in {in_file_name}: {e}')


def read_objects_from_stream(in_file: io.BytesIO, type_map, out_dict: Dict[bytes, Resource], use_buffering=False):
    while True:
        start_pos = in_file.tell()
        if not in_file.read(1):
            break
        in_file.seek(start_pos)
        type_hash, size = struct.unpack('<QI', in_file.read(12))
        in_file.seek(start_pos)
        if use_buffering:
            stream = io.BytesIO(in_file.read(12 + size))
        else:
            stream = in_file
        # check type map to see if we have a dedicated constructor
        little_endian_type = '{0:X}'.format(type_hash)
        type_info: List[Any] = ["Unknown"]
        if little_endian_type in type_map:
            type_info = type_map[little_endian_type]
        if len(type_info) > 1:
            parse_start_pos = stream.tell()

            try:
                specific_res = type_info[1](stream)
                out_dict[specific_res.uuid] = specific_res
            except:
                stream.seek(parse_start_pos)
                unknown_res = UnknownResource(stream)
                raise Exception("{} {} failed to parse"
                                .format(type_info[0], binascii.hexlify(unknown_res.uuid).decode('ASCII')))

            parse_end_pos = stream.tell()
            read_count = (parse_end_pos - parse_start_pos)
            if size + 12 != read_count:
                print("{} {} didn't match size, expected {}, read {}"
                      .format(specific_res.type, binascii.hexlify(specific_res.uuid).decode('ASCII'),
                              size + 12, read_count))
        else:
            unknown_res = UnknownResource(stream)
            out_dict[unknown_res.uuid] = unknown_res


class HashedString:
    def __init__(self, text_hash, text):
        self.text_hash = text_hash
        self.text = text

    def __str__(self):
        return self.text


def parse_hashed_string(stream: BinaryIO, include_hash=False):
    size = struct.unpack('<I', stream.read(4))[0]
    if size > 0:
        string_hash = stream.read(4)
    else:
        string_hash = bytes()
    if include_hash:
        return HashedString(string_hash, stream.read(size).decode('ASCII'))
    else:
        return stream.read(size).decode('ASCII')


def read_utf16_chars(stream: BinaryIO, length):
    # Read one byte at a time
    binary_chunks = iter(partial(stream.read, 1), "")
    # Convert bytes into unicode code points
    decoder = iterdecode(binary_chunks, 'utf_16_le')
    return str().join(islice(decoder, length))
