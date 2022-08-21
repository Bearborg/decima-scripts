import io
import os
import csv
import struct
import pydecima
import binascii
import argparse
from typing import Dict
from pydecima.enums import ETextLanguages
from pydecima.resources import LocalizedTextResource
from pydecima.type_maps import get_type_map

simpletext_header = ['UUID', 'Text', 'Translation']
language = ETextLanguages.English


def dump_core(core_path: str, csv_path: str):
    script_objects = {}
    pydecima.reader.read_objects(core_path, script_objects)
    with open(csv_path, 'w', newline='', encoding='utf8') as out_file:
        out = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        out.writerow(simpletext_header)
        for obj in script_objects.values():
            if isinstance(obj, LocalizedTextResource):
                out.writerow([binascii.hexlify(obj.uuid).decode('ASCII'), obj.language[language], ''])


def serialize_localized_text(text: LocalizedTextResource):
    output = text.uuid

    for lang in text.language:
        val = lang.encode('utf8')
        output += struct.pack('<H', len(val))
        output += val

    output = struct.pack('<QI', text.type_hash, len(output)) + output
    return output


def repack_core(core_path: str, csv_path: str):
    text_map: Dict[bytes, str] = dict()

    with open(csv_path, 'r', newline='', encoding='utf8') as csv_file:
        reader = iter(csv.reader(csv_file, quoting=csv.QUOTE_ALL))
        header = next(reader)
        assert(header == simpletext_header)
        for line in reader:
            if len(line[-1]) > 0:
                obj_hash = binascii.unhexlify(line[0])
                new_text = line[-1]
                text_map[obj_hash] = new_text

    with open(core_path, 'r+b') as core_file:
        orig_core = io.BytesIO(core_file.read())
        core_file.seek(0)
        core_file.truncate(0)
        while True:
            start = orig_core.tell()
            obj_type = orig_core.read(8)
            if len(obj_type) < 8:
                break
            str_type = '{0:X}'.format(struct.unpack('<Q', obj_type)[0])
            obj_size = struct.unpack('<I', orig_core.read(4))[0]
            obj_uuid = orig_core.read(16)
            orig_core.read(obj_size)

            type_map = get_type_map(pydecima.reader.decima_version)
            if type_map[str_type] == 'LocalizedTextResource' and obj_uuid in text_map:
                script_objects = {}
                orig_core.seek(start)
                resource_stream = io.BytesIO(orig_core.read(obj_size + 12))
                pydecima.reader.read_objects_from_stream(resource_stream, script_objects)
                assert(len(script_objects) == 1)
                text = script_objects[obj_uuid]
                text.language[language] = text_map[obj_uuid]
                serialized_text = serialize_localized_text(text)
                core_file.write(serialized_text)
            else:
                # Copy data without modifying
                orig_core.seek(start)
                core_file.write(orig_core.read(obj_size + 12))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--dump', type=str,
                       help="Path to a core file to dump.")
    group.add_argument('-r', '--repack', type=str,
                       help="Path to a core file to repack.")
    args = parser.parse_args()

    game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')
    pydecima.reader.set_globals(_game_root_file=game_root_file, _decima_version='HZDPC')

    if args.dump:
        csv_path = os.path.splitext(args.dump)[0] + '.csv'
        assert os.path.isfile(args.dump)
        dump_core(args.dump, csv_path)
        print('CSV file generated.')
    elif args.repack:
        csv_path = os.path.splitext(args.repack)[0] + '.csv'
        assert os.path.isfile(args.repack)
        repack_core(args.repack, csv_path)
        print('Updated text repacked into core.')


if __name__ == '__main__':
    main()
