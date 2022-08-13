#Text Repacker

##Prerequisites
In order to use this tool, you will need:

1. Python 3.7 or higher (lower versions of Python 3.x may also work- I haven't checked).
2. Extracted .core files from Death Stranding's .bin archives. I recommend using 
   [Decima Explorer](https://github.com/Jayveer/Decima-Explorer), but other tools may work too.

## Running the script
To dump a .core file to CSV format, run the script with the -d (or --dump) parameter set to your .core file:

`python text_repacker.py -d "C:\HZD\localized\sentences\aigenerated\aloy\sentences.core"`

The CSV file will be automatically placed in the same directory as the .core file. To add translations, fill out the
Translations column of the CSV. _Do not edit the text in the Text column_, as this will not change the contents of the
.core file.

Once you've made your translations, you can repack your new text into the .core by running the script with the
-r (or --repack) parameter set to your .core file:

`python text_repacker.py -r "C:\HZD\localized\sentences\aigenerated\aloy\sentences.core"`

As long as the CSV file is in the same folder as the .core, the translated text will replace the original contents.