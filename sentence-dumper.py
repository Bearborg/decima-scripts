import struct
import sys
from functools import partial
from typing import List

import decima
import os
import yaml

sentence_file =\
    r'E:\Game Files\HZDCE\Image0\packed_pink\localized\sentences\mq15_themountainthatfell\mq15_audiologs\sentences.core'


def localized_text_representer(dumper: yaml.Dumper, localized_text: decima.LocalizedTextResource):
    return dumper.represent_str(localized_text.english)


def dump_simpletext(filename):
    print(filename)
    script_objects = {}
    decima.read_objects(filename, script_objects)

    out = ''
    yaml.add_representer(decima.LocalizedTextResource, localized_text_representer)

    collections = [v for v in script_objects.values() if isinstance(v, decima.ObjectCollection)]
    assert len(collections) <= 1
    if len(collections) == 1:
        texts = map(lambda v: v.follow(script_objects), collections[0].objects)
    else:
        texts = script_objects.values()
    for text in texts:
        if not isinstance(text, decima.LocalizedTextResource):
            print('{} in {} is not a LocalizedTextResource, skipping'.format(text, filename))
            continue
        text: decima.LocalizedTextResource
        lines = text.english.split('\n')
        if len(lines) > 1:
            out += '- |-\n'
            for line in lines:
                out += '  {}\n'.format(line)
        else:
            out += yaml.dump([text], allow_unicode=True, width=sys.maxsize)

    with open(filename + '.yml', 'w', encoding='utf8') as out_file:
        out_file.write(out)


def dump_sentences(filename):
    print(filename)
    script_objects = {}
    decima.read_objects(filename, script_objects)

    out = ''
    visited_uuids = set()
    file_objects = script_objects.copy()

    groups = [n for n in script_objects.values() if isinstance(n, decima.SentenceGroupResource)]
    groups.sort(key=lambda group: group.name)

    for x in groups:
        out += '- {}: # {}\n'.format(x.name, x.type)
        out += '   Order: {}\n'.format(x.sentence_type.name)
        for sentence in x.sentences:
            sent = sentence.follow(script_objects)
            visited_uuids.add(sent.uuid)
            out += '   {}: # {}\n'.format(sent.name, sent.type)
            text = sent.text.follow(script_objects)
            if text is not None:
                visited_uuids.add(text.uuid)
            out += '    {}: {}\n'.format(
                sent.voice.follow(script_objects).text.follow(script_objects),
                text.english.__repr__() if sent.text.type != 0 else '<No subtitle>'
            )
        out += '\n'

    found_orphans = False
    for t in file_objects.values():
        if t.type in ['SentenceResource', 'LocalizedTextResource'] and t.uuid not in visited_uuids:
            if not found_orphans:
                found_orphans = True
                out += '- Orphaned data:\n'
            assert(t.type == 'LocalizedTextResource')
            t: decima.LocalizedTextResource
            out += '  - {}\n'.format(t.english.__repr__())

    with open(filename + '.yml', 'w', encoding='utf8') as out_file:
        out_file.write(out)


def dump_recursive(directory):
    for root, directories, filenames in os.walk(directory):
        for f in filenames:
            if os.stat(os.path.join(root, f)).st_size > 0:  # Ignore empty files
                if f == "simpletext.core":
                    dump_simpletext(os.path.join(root, f))
                elif f == "sentences.core":
                    dump_sentences(os.path.join(root, f))
                elif f.endswith(".core"):
                    print("Non-matching name: " + os.path.join(root, f))


def dump_audio(filename):
    print(filename)
    script_objects = {}
    decima.read_objects(filename, script_objects)
    sentences = [x for x in script_objects.values() if isinstance(x, decima.SentenceResource)]

    sentences.sort(key=lambda sent: sent.sound.follow(script_objects).sound_info[0].start)

    sound_dir = os.path.join(os.path.split(filename)[0], 'sentences.english')
    assert (os.path.isfile(sound_dir + '.stream'))
    if not os.path.isdir(sound_dir):
        os.mkdir(sound_dir)
    sound_stream = open(sound_dir + '.stream', 'rb')
    for s in range(len(sentences)):
        sound = sentences[s].sound.follow(script_objects)

        print('{}: {} + {} = {}'.format(sentences[s].name, sound.sound_info[0].start, sound.sound_info[0].size_1,
                                        sound.sound_info[0].start + sound.sound_info[0].size_1))

        if s > 0:
            prev_sound = sentences[s - 1].sound.follow(script_objects)
            if sound.sound_info[0].start != prev_sound.sound_info[0].start + prev_sound.sound_info[0].size_1:
                print('possible duplicate sound, {}: {}'.format(filename, sentences[s].name))

        ext = 'mp3' if sound.unk_bytes_5[1] == 0x0b else 'at9'
        sound_filename = os.path.join(sound_dir, '{}.{}'.format(sentences[s].name, ext))
        sound_stream.seek(sound.sound_info[0].start)
        sound_data = sound_stream.read(sound.sound_info[0].size_1)
        with open(sound_filename, 'wb') as sound_out_file:
            sound_out_file.write(sound_data)


#dump_recursive(r'E:\Game Files\HZDPC\localized\sentences')
# dump_sentences(sentence_file)
# dump_simpletext(r'E:\Game Files\HZDPC\localized\sentences\mq15_themountainthatfell\mq15_simpletext\simpletext.core')
dump_audio(r'E:\Game Files\HZDPC\localized\sentences\tnd10_gerashusband\tnd10_ic_gerakendert\sentences.core')
