import argparse
import os
from typing import Dict
import pydecima
from pydecima.resources import MusicResource, Resource

game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')
script_objects: Dict[bytes, Resource] = {}


def dump_world_music(out_dir):
    pydecima.reader.set_globals(_game_root_file=game_root_file, _decima_version='HZDPC')
    music_file = os.path.join(pydecima.reader.game_root, r'sounds/music/world/world.core')
    assert os.path.isfile(music_file), f"Could not find {music_file}"
    pydecima.reader.read_objects(music_file, script_objects)

    for obj in script_objects.values():
        if obj.type == 'MusicResource':
            obj: MusicResource
            meda: MusicResource.MEDASection = obj.section_struct.sections["MEDA"]
            stream_paths = [x.cache_string for x in obj.cache_structs]
            streams = []
            for stream in stream_paths:
                assert stream.startswith("cache:")
                stream_file = os.path.join(pydecima.reader.game_root, stream[6:])
                assert os.path.isfile(stream_file), f"Could not find {stream_file}"
                streams.append(stream_file)
            filenames = list(filter(lambda text: text.endswith(".mp3"), obj.section_struct.sections["STRL"]))
            assert len(filenames) == len(meda.offsets)
            stream_index = -1
            curr_stream = None
            for filename, music in zip(filenames, meda.offsets):
                if music.offset == 0:
                    # Start of a new stream file; close previous stream and open new one
                    if curr_stream:
                        curr_stream.close()
                    stream_index += 1
                    curr_stream = open(streams[stream_index], 'rb')
                print(f'{streams[stream_index]}: {filename}')
                out_file = open(os.path.join(out_dir, filename), 'wb')
                curr_stream.seek(music.offset)
                out_file.write(curr_stream.read(music.size))
                out_file.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Directory path to place dumped ambient music into.")
    args = parser.parse_args()
    if not os.path.isdir(args.path):
        raise Exception(f'"{args.path}" is not an existing directory.')
    dump_world_music(args.path)


if __name__ == "__main__":
    main()
