from typing import Optional
import pydecima
import os
import argparse

from pydecima.enums import EAudioLanguages, ETextLanguages
from pydecima.resources import LocalizedTextResource, SentenceGroupResource, SentenceResource, ObjectCollection


def yaml_one_line_string(text: str, prefer_quotes=False):
    indicators = ('-', '?', ':', ',', '[', ']', '{', '}', '#', '&', '*', '!', '|', '>', '\'', '"', '%', '@', '`', ' ')
    if not prefer_quotes and ': ' not in text and '#' not in text and not text.startswith(indicators):  # plain string
        return text
    else:  # double-quoted string
        return '"{}"'.format(text.replace("\\", "\\\\").replace('"', '\\"').replace('\n', '\\n'))


def get_localized_text_yaml(text: LocalizedTextResource, language: ETextLanguages):
    out = ''
    lines = text.language[language].split('\n')
    if len(lines) > 1:
        out += '- |-\n'
        for line in lines:
            out += '  {}\n'.format(line)
    else:
        out += "- " + yaml_one_line_string(text.language[language]) + '\n'
    return out


def dump_simpletext(filename, language: ETextLanguages):
    print(filename)
    script_objects = {}
    pydecima.reader.read_objects(filename, script_objects)

    out = ''

    collections = [v for v in script_objects.values() if isinstance(v, ObjectCollection)]
    assert len(collections) <= 1
    if len(collections) == 1:
        texts = map(lambda v: v.follow(script_objects), collections[0].objects)
    else:
        texts = script_objects.values()
    for text in texts:
        if not isinstance(text, LocalizedTextResource):
            print(f'{text} in {filename} is not a LocalizedTextResource, skipping')
            continue
        text: LocalizedTextResource
        out += get_localized_text_yaml(text, language)

    with open(filename + '.yml', 'w', encoding='utf8') as out_file:
        out_file.write(out)


def dump_sentences(filename, language: ETextLanguages):
    script_objects = {}
    pydecima.reader.read_objects(filename, script_objects)

    out = ''
    visited_uuids = set()
    file_objects = script_objects.copy()

    groups = [n for n in script_objects.values() if isinstance(n, SentenceGroupResource)]
    groups.sort(key=lambda group: group.name)

    for x in groups:
        out += f'- {x.name}: # {x.type}\n'
        out += f'   Order: {x.sentence_type.name}\n'
        for sentence in x.sentences:
            sent = sentence.follow(script_objects)
            visited_uuids.add(sent.uuid)
            out += f'   {yaml_one_line_string(sent.name)}: # {sent.type}\n'
            text = sent.text.follow(script_objects)
            if text is not None:
                visited_uuids.add(text.uuid)
            voice_name = sent.voice.follow(script_objects).text.follow(script_objects)
            voice_str = '<No voice name>'
            if voice_name.language[language] != '':
                voice_str = voice_name.language[language]
            elif voice_name.language[ETextLanguages.English] != '':
                voice_str = voice_name.language[ETextLanguages.English]
            out += '    {}: {}\n'.format(
                yaml_one_line_string(voice_str),
                yaml_one_line_string(text.language[language], True) if sent.text.type != 0 else '<No subtitle>'
            )
        out += '\n'

    found_orphans = False
    for t in file_objects.values():
        if t.type in ['SentenceResource', 'LocalizedTextResource'] and t.uuid not in visited_uuids:
            if not found_orphans:
                found_orphans = True
                out += '- Orphaned data:\n'
            assert(t.type == 'LocalizedTextResource')
            t: LocalizedTextResource
            loc = t.language[language] if t.language[language] != "" else t.language[ETextLanguages.English]
            out += f'  - {yaml_one_line_string(loc, True)}\n'

    with open(filename + '.yml', 'w', encoding='utf8') as out_file:
        out_file.write(out)


def dump_file(filename: str, do_audio: bool, do_text: bool,
              audio_lang: EAudioLanguages, text_lang: ETextLanguages):
    if os.stat(filename).st_size > 0:  # Ignore empty files
        f = os.path.split(filename)[-1]
        if f == "simpletext.core":
            if do_text:
                print(filename)
                dump_simpletext(filename, text_lang)
        elif f == "sentences.core":
            print(filename)
            if do_text:
                dump_sentences(filename, text_lang)
            if do_audio:
                dump_audio(filename, audio_lang)
        elif f.endswith(".core"):
            print("Unrecognized filename: " + filename)


def dump_recursive(directory: str, do_audio: bool, do_text: bool,
                   audio_lang: EAudioLanguages, text_lang: ETextLanguages):
    for root, directories, filenames in os.walk(directory):
        for f in filenames:
            dump_file(os.path.join(root, f), do_audio, do_text, audio_lang, text_lang)


def dump_audio(filename, language: EAudioLanguages):
    script_objects = {}
    pydecima.reader.read_objects(filename, script_objects)
    sentences = [x for x in script_objects.values() if isinstance(x, SentenceResource) and
                 x.sound.follow(script_objects).sound_info[language] is not None]
    missing_sentences = [x for x in script_objects.values() if isinstance(x, SentenceResource) and
                         x.sound.follow(script_objects).sound_info[language] is None]
    for s in missing_sentences:
        print(f'{s.name} has no audio in language {language.name}, skipping')

    if len(sentences) == 0:
        return

    sentences.sort(key=lambda sent: sent.sound.follow(script_objects).sound_info[language].start)

    sound_dir = os.path.join(os.path.split(filename)[0], 'sentences.' + language.name.lower())
    assert (os.path.isfile(sound_dir + '.stream')),\
        f"Cannot dump audio, missing required file {sound_dir}.stream"
    if not os.path.isdir(sound_dir):
        os.mkdir(sound_dir)
    sound_stream = open(sound_dir + '.stream', 'rb')
    for s in range(len(sentences)):
        sound = sentences[s].sound.follow(script_objects)
        if s > 0:
            prev_sound = sentences[s - 1].sound.follow(script_objects).sound_info[language]
            curr_sound = sound.sound_info[language]
            if curr_sound.start == prev_sound.start:
                print(f'Duplicate sound, {filename}: {sentences[s].name} is identical to {sentences[s - 1].name}')
            elif curr_sound.start > prev_sound.start + prev_sound.size_1:
                print('Unused sound in {}.stream, between {} and {}'.format(
                    sound_dir, prev_sound.start + prev_sound.size_1, curr_sound.start))
            else:
                assert curr_sound.start >= prev_sound.start + prev_sound.size_1,\
                    f"Overlapping sound files, {filename} is likely broken"
        ext = 'vgmstream'
        if sound.audio_type == 0x0b:
            ext = 'mp3'
        elif sound.audio_type == 0x09 or sound.audio_type == 0x0d:
            ext = 'at9'
        elif sound.audio_type == 0x0f:  # ps4-only
            ext = 'aac'
        sound_filename = os.path.join(sound_dir, f'{sentences[s].name}.{ext}')
        sound_stream.seek(sound.sound_info[language].start)
        sound_data = sound_stream.read(sound.sound_info[language].size_1)

        with open(sound_filename, 'wb') as sound_out_file:
            sound_out_file.write(sound_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--language", type=str, help="The language to output text/audio in.",
                        choices=[lang.name for lang in ETextLanguages], default='English')
    parser.add_argument("-d", "--dump", type=str.lower, help="Which type of output to dump; text, audio, or all.",
                        choices=['text', 'audio', 'all'], default='all')
    parser.add_argument("path", type=str,
                        help="Path to a sentences.core/simpletext.core file, or a directory to recursively dump from.")
    args = parser.parse_args()
    text_language: ETextLanguages = getattr(ETextLanguages, args.language)

    language_lookup = {
        'Portuguese': EAudioLanguages.Portugese,
        'LatinAmericanSpanish': EAudioLanguages.LatAmSp,
        'BrazilianPortuguese': EAudioLanguages.LatAmPor
    }
    audio_language: Optional[EAudioLanguages]
    if hasattr(EAudioLanguages, text_language.name):
        audio_language = getattr(EAudioLanguages, text_language.name)
    elif text_language.name in language_lookup:
        audio_language = language_lookup[text_language.name]
    else:
        audio_language = None

    audio = args.dump in ['audio', 'all']
    text = args.dump in ['text', 'all']

    if audio and audio_language is None:
        print(f'Language {text_language.name} does not have audio; disabling audio dumping.')
        audio = False

    game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')
    pydecima.reader.set_globals(_game_root_file=game_root_file, _decima_version='HZDPC')

    if os.path.isfile(args.path):
        dump_file(args.path, audio, text, audio_language, text_language)
    elif os.path.isdir(args.path):
        dump_recursive(args.path, audio, text, audio_language, text_language)
    else:
        raise Exception(f'"{args.path}" is not a file or directory.')


if __name__ == '__main__':
    main()
