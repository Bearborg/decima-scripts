# Sound Dumper

## Prerequisites
In order to use this tool, you will need:

1. Python 3.7 or higher (lower versions of Python 3.x may also work- I haven't checked).
2. The PyDecima package, installed by running `pip install pydecima`
3. Extracted .core files from Horizon Zero Dawn's .bin archives. I recommend using 
   [Decima Explorer](https://github.com/Jayveer/Decima-Explorer), but other tools may work too.

Before running the script, you will also need to provide the root directory of your game files. Edit 
`hzd_root_path.txt` to contain the root path where your extracted game files are located (e.g. if you have extracted
the "textures" folder to the location `C:\HZD\textures`, you should put `C:\HZD`).

## Running the script
The simplest way to run the dumper is by providing only a path to a .core file:

`python sound_dumper.py "C:\HZD\sounds\effects\robots\scout\scout_main\wav\vox_alerted_transition_a_1.core"`

This will dump all sound effects contained in the file.

You can also provide a directory path:

`python texture_dumper.py "C:\HZD\sounds\effects\robots\scout\scout_main"`

This will dump all sound effects for any .core files in the directory, or in its subdirectories.