import io
import os
import json
import struct
import binascii
import argparse
from typing import Dict
import ds_decima as decima


simpletext_header = ['UUID', 'Text', 'Translation']
language = decima.ETextLanguages.English


def dump_core(core_path: str, json_path: str):
    script_objects = {}
    decima.read_objects(core_path, script_objects)
    out_list = []
    for obj in script_objects.values():
        if isinstance(obj, decima.LocalizedTextResource):
            out_list.append({
                'uuid': binascii.hexlify(obj.uuid).decode('ASCII'),
                'text': obj.language[language].text,
                'translation': ''})
    with open(json_path, 'w', encoding='utf8') as out_file:
        out_file.write(json.dumps(out_list, indent=2, ensure_ascii=False))


def serialize_localized_text(text: decima.LocalizedTextResource):
    output = text.uuid

    for lang in text.language:
        val = lang.text.encode('utf8')
        output += struct.pack('<H', len(val))
        output += val
        output += lang.unks

    output = struct.pack('<QI', text.type_hash, len(output)) + output
    return output


def repack_core(core_path: str, json_path: str):
    text_map: Dict[bytes, str] = dict()

    with open(json_path, 'r', encoding='utf8') as json_file:
        contents = json.loads(json_file.read())
        for line in contents:
            obj_hash = binascii.unhexlify(line['uuid'])
            new_text = line['translation']
            text_map[obj_hash] = new_text if new_text != '' else line['text']

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

            if str_type in decima.pc_type_map and decima.pc_type_map[str_type][0] == 'LocalizedTextResource'\
                    and obj_uuid in text_map:
                script_objects = {}
                orig_core.seek(start)
                resource_stream = io.BytesIO(orig_core.read(obj_size + 12))
                decima.read_objects_from_stream(resource_stream, decima.pc_type_map, script_objects)
                assert(len(script_objects) == 1)
                text = script_objects[obj_uuid]
                text.language[language].text = text_map[obj_uuid]
                serialized_text = serialize_localized_text(text)
                core_file.write(serialized_text)
            else:
                # Copy data without modifying
                orig_core.seek(start)
                core_file.write(orig_core.read(obj_size + 12))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dump', type=str,
                       help="Path to a core file to dump.")
    group.add_argument('-r', '--repack', type=str,
                       help="Path to a core file to repack.")
    args = parser.parse_args()
    if args.dump:
        json_path = os.path.splitext(args.dump)[0] + '.json'
        assert os.path.isfile(args.dump)
        dump_core(args.dump, json_path)
        print('JSON file generated.')
    elif args.repack:
        json_path = os.path.splitext(args.repack)[0] + '.json'
        assert os.path.isfile(args.repack)
        repack_core(args.repack, json_path)
        print('Updated text repacked into core.')


if __name__ == '__main__':
    main()
