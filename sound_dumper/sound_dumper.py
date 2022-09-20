import pydecima
import os
from typing import Dict
import wave
import argparse

from pydecima.enums import EWaveDataEncoding
from pydecima.resources import Resource, WaveResource, MusicResource


def unwrap_audio(in_file_path):
    print(f'Dumping audio from {in_file_path}')
    script_objects: Dict[bytes, Resource] = {}
    pydecima.reader.read_objects(in_file_path, script_objects)
    dumped_count = 0
    out_file_dir, filename = os.path.split(in_file_path)
    base_filename = os.path.splitext(filename)[0]

    for obj_id in script_objects:
        obj = script_objects[obj_id]
        if isinstance(obj, WaveResource):
            wave_obj: WaveResource = obj
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
        elif isinstance(obj, MusicResource):
            music_obj: MusicResource = obj
            meda: MusicResource.MEDASection = music_obj.section_struct.sections["MEDA"]
            stream_paths = [x.cache_string for x in music_obj.cache_structs]
            streams = []
            for stream in stream_paths:
                assert stream.startswith("cache:")
                stream_file = os.path.join(pydecima.reader.game_root, stream[6:])
                assert os.path.isfile(stream_file), f"Could not find {stream_file}"
                streams.append(stream_file)
            filenames = list(filter(lambda text: text.endswith(".mp3"), music_obj.section_struct.sections["STRL"]))
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
                out_file = open(os.path.join(out_file_dir, filename), 'wb')
                curr_stream.seek(music.offset)
                out_file.write(curr_stream.read(music.size))
                out_file.close()
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
