import binascii
import struct
import os
import io
from enum import IntEnum

from typing import Dict, BinaryIO, TypeVar, Generic, List, Any

script_dir = os.path.dirname(__file__)
pc_path_file = os.path.join(script_dir, r'hzd_root_path.txt')
game_root_pc = open(pc_path_file, 'r').read().strip('" \t\r\n') if os.path.isfile(pc_path_file) else ''
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
    SimplifiedChinese = 20,
    English2 = 21,
    Greek = 22,
    Czech = 23,
    Hungarian = 24


class Resource:
    def __init__(self, stream: BinaryIO):
        self.type_hash = struct.unpack('<Q', stream.read(8))[0]
        little_endian_type = '{0:X}'.format(self.type_hash)
        type_map = pc_type_map
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
            game_root = game_root_pc
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
        # if self.uuid[:2] == b'\x00\x00':
        #     print('{} likely has starting short'.format(self.type))
        #     stream.seek(start_pos + 14)
        #     self.uuid = stream.read(16)
        stream.seek(start_pos)
        self.data = stream.read(self.size + 12)


class LocalizedTextResource(Resource):
    class Localization:
        def __init__(self, stream: BinaryIO):
            self.size = struct.unpack('<H', stream.read(2))[0]
            self.text = stream.read(self.size).decode('UTF8')
            self.unks = stream.read(3)

    def __init__(self, stream: BinaryIO):
        Resource.__init__(self, stream)
        self.language: List[LocalizedTextResource.Localization] \
            = [LocalizedTextResource.Localization(stream) for _ in ETextLanguages]

    def __str__(self):
        return self.language[ETextLanguages.English].text.strip()

    def __repr__(self):
        return self.language[ETextLanguages.English].text.__repr__()


pc_type_map = {'31BE502435317445': ["LocalizedTextResource", LocalizedTextResource]}


def read_objects(in_file_name: str, out_dict: Dict[bytes, Resource], use_buffering=False):
    type_map = pc_type_map

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
                raise Exception("{} {} didn't match size, expected {}, read {}"
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
