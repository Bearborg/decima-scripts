import invoke
import os
import sys
import argparse
from decima import game_root_pc

script_dir = os.path.dirname(__file__)
stream_files_dict = eval(open(os.path.join(script_dir, r'language_stream_contents.txt'), 'r').read())


def extract_file(bin_file, filename, out_file, deci_exp):
    invoke.run(f'"{deci_exp}" -e "{bin_file}" "{filename}" "{out_file}"')


def dump_bins(archive, deci_exp):
    bin_file = os.path.split(archive)[1]
    filenames = stream_files_dict[bin_file]
    for i in range(len(filenames)):
        file = filenames[i]
        out_file = os.path.join(game_root_pc, file)
        try:
            print(f'{bin_file} {i + 1}/{len(filenames)}')
            extract_file(archive, file, out_file, deci_exp)
        except:
            print(f"failed to extract: {out_file}", file=sys.stderr)


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
    if filename not in stream_files_dict:
        print(f"Filename {filename} is not a recognized HZD language file")
        exit(1)
    print(f"Dumping bin {filename}")
    dump_bins(args.path_to_bin, args.path_to_decima_explorer)


if __name__ == '__main__':
    main()
