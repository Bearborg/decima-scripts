import pydecima
import os
from typing import Dict
import wave
import argparse

from pydecima.enums import EWaveDataEncoding
from pydecima.resources import Resource, WaveResource


def unwrap_audio(in_file_path):
    print(f'Dumping audio from {in_file_path}')
    script_objects: Dict[bytes, Resource] = {}
    pydecima.reader.read_objects(in_file_path, script_objects)
    dumped_count = 0
    for obj in script_objects:
        wave_obj = script_objects[obj]
        if isinstance(wave_obj, WaveResource):
            if wave_obj.size_with_stream == wave_obj.size_without_stream:
                sound_data = wave_obj.sound
            else:
                assert wave_obj.size_without_stream == 0, "WaveResource has both streamed and unstreamed data"
                assert wave_obj.cache_string.startswith("cache:")
                stream_path = os.path.join(pydecima.reader.game_root, wave_obj.cache_string[6:])
                if not os.path.isfile(stream_path):
                    print(f'Missing stream at {stream_path}, skipping')
                    continue
                stream_file = open(stream_path, 'rb')
                sound_data = stream_file.read(wave_obj.size_with_stream)

            ext = ".vgmstream"
            if wave_obj.encoding == EWaveDataEncoding.PCM:
                ext = ".wav"
            elif wave_obj.encoding == EWaveDataEncoding.AAC:
                ext = ".aac"
            elif wave_obj.encoding == EWaveDataEncoding.ATRAC9:
                ext = ".at9"
            elif wave_obj.encoding == EWaveDataEncoding.MP3:
                ext = ".mp3"
            out_file_dir, filename = os.path.split(in_file_path)
            base_filename = os.path.splitext(filename)[0]
            out_filename = base_filename + ext if len(script_objects) == 1 else wave_obj.name + ext
            out_file_path = os.path.join(out_file_dir, out_filename)

            # Special case for PCM audio, need to construct a WAV header
            if wave_obj.encoding == EWaveDataEncoding.PCM:
                with wave.open(out_file_path, 'wb') as out_file:
                    out_file.setnchannels(wave_obj.channels)
                    out_file.setsampwidth(2)
                    out_file.setframerate(wave_obj.sample_rate)
                    out_file.writeframes(sound_data)
                dumped_count += 1
                continue

            with open(out_file_path, 'wb') as out_file:
                out_file.write(sound_data)
                dumped_count += 1
    print(f'Dumped {dumped_count} sound{"s" if dumped_count != 1 else ""}')


def dump_recursive(directory: str):
    for root, directories, filenames in os.walk(directory):
        for f in filenames:
            if os.path.splitext(f)[1] == ".core":
                unwrap_audio(os.path.join(root, f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str,
                        help="Path to a .core file containing audio, or a directory to recursively dump from.")
    args = parser.parse_args()

    game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')
    pydecima.reader.set_globals(_game_root_file=game_root_file, _decima_version='HZDPC')

    if os.path.isfile(args.path) and os.path.splitext(args.path)[1] == ".core":
        unwrap_audio(args.path)
    elif os.path.isdir(args.path):
        dump_recursive(args.path)
    else:
        raise Exception(f'"{args.path}" is not a .core file or a directory.')


if __name__ == "__main__":
    main()
