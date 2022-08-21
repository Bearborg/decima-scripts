import invoke
import os
import sys
import argparse
import pydecima
from language_stream_contents import language_stream_contents

script_dir = os.path.dirname(__file__)
game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')
pydecima.reader.set_globals(_game_root_file=game_root_file)


def extract_file(bin_file, filename, out_file, deci_exp):
    invoke.run(f'"{deci_exp}" -e "{bin_file}" "{filename}" "{out_file}"')


def dump_bins(archive, deci_exp):
    bin_file = os.path.split(archive)[1]
    filenames = language_stream_contents[bin_file]
    for i in range(len(filenames)):
        file = 'localized/sentences/' + filenames[i]
        out_file = os.path.join(pydecima.reader.game_root, file)
        try:
            print(f'{bin_file} {i + 1}/{len(filenames)}')
            extract_file(archive, file, out_file, deci_exp)
        except Exception as e:
            print(f"failed to extract {out_file} with error {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_bin", type=str,
                        help="Path to a language-specific .bin file.")
    parser.add_argument("path_to_decima_explorer", type=str,
                        help="Path to the Decima Explorer executable file.")
    args = parser.parse_args()
    if not os.access(args.path_to_decima_explorer, os.X_OK):
        print(f"Provided path to Decima Explorer is not an executable file")
        exit(1)
    filename = os.path.split(args.path_to_bin)[1]
    if filename not in language_stream_contents:
        print(f"Filename {filename} is not a recognized HZD language file")
        exit(1)
    print(f"Dumping bin {filename}")
    dump_bins(args.path_to_bin, args.path_to_decima_explorer)


if __name__ == '__main__':
    main()
