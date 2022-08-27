# Sentence Dumper

## Prerequisites
In order to use this tool, you will need:

1. Python 3.7 or higher (lower versions of Python 3.x may also work- I haven't checked).
2. An extracted "localized" directory from Horizon Zero Dawn's .bin
   archives. I recommend using [Decima Explorer](https://github.com/Jayveer/Decima-Explorer), but other tools may work
   too.

Before running the script, you will also need to provide the root directory of your game files. Edit 
`hzd_root_path.txt` to contain the path where your "localized" folder is located (e.g. if your localized folder is at
`C:\HZD\localized` you should put `C:\HZD`).

Finally, to dump audio, you'll need to extract the contents of your desired language's .bin archives- e.g. for english, 
you would want to extract DLC1_English.bin, Initial_English.bin, and Remainder_English.bin.

Unfortunately, Decima Explorer will **not** dump these files by default. For convenience, I've included another script
which will use Decima Explorer to extract these files, `dump_language_streams.py`. You'll need to pass it the path of
the bin file you want to extract, followed by the path to the Decima Explorer executable:

`python dump_language_streams.py "E:\Games\SteamApps\common\Horizon Zero Dawn\Packed_DX12\Initial_English.bin" "C:\Tools\Decima Explorer\DecimaExplorer.exe"`

The script will output the files to the root directory specified in `hzd_root_path.txt`, so make sure you've filled
that out first.

## Running the script
The simplest way to run the dumper is by providing only a path to a sentences.core or simpletext.core file:

`python sentence_dumper.py "C:\HZD\localized\sentences\aigenerated\aloy\sentences.core"`

This will dump all english audio and text for that file.

You can also provide a directory path:

`python sentence_dumper.py "C:\HZD\localized\sentences\aigenerated"`

This will dump all english audio and text for any sentences.core/simpletext.core files in the directory, or in its
subdirectories.

### Languages
To dump a different language, use the `--language` or `-l` flag:

`python sentence_dumper.py -l Russian "C:\HZD\localized\sentences\aigenerated\aloy\sentences.core"`

The possible language choices are English, French, Spanish, German, Italian, Dutch, Portuguese, TraditionalChinese,
Korean, Russian, Polish, Danish, Finnish, Norwegian, Swedish, Japanese, LatinAmericanSpanish, BrazilianPortuguese,
Turkish, Arabic, and SimplifiedChinese.

This parameter is case-sensitive.

### What to dump
To dump only audio or only text, use the `--dump` or `-d` flag:

`python sentence_dumper.py -d audio "C:\HZD\localized\sentences\aigenerated\aloy\sentences.core"`

The possible choices are "text", "audio", or "all" (the default).


