import argparse
import decima
import struct
import os
from pathlib import PurePath
from typing import Dict


class PrefetchPathInfo:
    def __init__(self, path_hash, size):
        self.path_hash = path_hash
        self.size = size


def regenerate_prefetch(prefetch_file: str, output_file: str):
    script_objects = {}
    decima.read_objects(prefetch_file, script_objects)
    assert (len(script_objects) == 1)
    prefetch: decima.PrefetchList = next(iter(script_objects.values()))
    # Note: In Python versions <3.6, order may be incorrect
    prefetch_dict: Dict[str, PrefetchPathInfo] = {path.text: PrefetchPathInfo(path.text_hash, prefetch.sizes[i])
                                                  for i, path in enumerate(prefetch.paths)}

    for root, dirs, files in os.walk(decima.game_root_pc):
        for file in files:
            if not file.endswith('.core'):
                continue
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, decima.game_root_pc)
            path_without_ext = os.path.splitext(relative_path)[0]
            final_path = PurePath(path_without_ext).as_posix()
            if final_path in prefetch_dict:
                if os.stat(full_path).st_size != prefetch_dict[final_path].size:
                    print(f'{final_path} {prefetch_dict[final_path].size} -> {os.stat(full_path).st_size}')
                    prefetch_dict[final_path].size = os.stat(full_path).st_size

    # Write prefetch file
    with open(output_file, 'w+b') as out:
        out.write(struct.pack('<QI', prefetch.type_hash, 0))  # Placeholder length, need to update at end
        out.write(prefetch.uuid)
        out.write(struct.pack('<I', len(prefetch_dict)))
        for key in prefetch_dict.keys():
            out.write(struct.pack('<I', len(key)))
            out.write(prefetch_dict[key].path_hash)
            out.write(key.encode('ASCII'))
        out.write(struct.pack('<I', len(prefetch_dict)))
        for val in prefetch_dict.values():
            out.write(struct.pack('<I', val.size))
        out.write(struct.pack('<I', len(prefetch.indices)))
        for index in prefetch.indices:
            out.write(struct.pack('<I', index))
        final_size = out.tell() - 12
        out.seek(8)
        out.write(struct.pack('<I', final_size))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True,
                        help="Path to a prefetch file to update.")
    parser.add_argument('-o', '--output', type=str, required=True,
                        help="Path for updated prefetch file to be written.")
    args = parser.parse_args()
    regenerate_prefetch(args.input, args.output)


if __name__ == '__main__':
    main()

