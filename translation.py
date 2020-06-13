import json
import os
import sys
from gooey import Gooey, GooeyParser
from argparse import ArgumentParser


def load_json(filename):
    data = {}
    try:
        with open(filename, 'r', encoding="utf-8") as infile:
            data = json.load(infile)
    except FileNotFoundError:
        print("file {} not found".format(os.path.abspath(filename)))

    return data


def save_json(filename, data):
    try:
        with open(filename, 'w', encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
    except FileNotFoundError:
        print("file {} not found".format(os.path.abspath(filename)))


def replace_values(json_data, mapping, keys, path=''):
    for k in json_data:
        e = json_data[k]
        p = path + '.' + k
        
        # first check id we must replace the entry
        if p in keys:
            if json_data[k] in mapping:
                json_data[k] = mapping[e]
            else:
                print("no mapping found for {} read '{}'".format(e, p))
                
        if type(e) is dict:
            replace_values(json_data[k], mapping, keys, p)
            
        if type(e) is list:
            for i in e:
                replace_values(i, mapping, keys, p)


def add_arguments(parser):
    parser.add_argument(
        '-p',
        '--project',
        action="store",
        metavar="Project File",
        required=True,
        widget="FileChooser",
        help="Select the general project json-file with translation keys."
    )
    parser.add_argument(
        '-t',
        '--translation',
        action="store",
        metavar="Translation File",
        required=True,
        widget="FileChooser",
        help="Select the translation file (json with key/value pairs)."
    )
    parser.add_argument(
        '-k',
        '--key-list',
        action="store",
        metavar="List of Replaceable Paths",
        required=False,
        default=".canvas.name",
        help="Comma separated list of keys which can be translated"
    )

@Gooey(
    program_name="Json-Translator",
    optional_cols=1
)
def interview_arguments():
    parser = GooeyParser(
        description="Replace all keys from translation file find in given json-path."
    )

    pg = parser.add_argument_group()
    add_arguments(pg)
    return parser.parse_args()


def parse_arguments():
    parser = ArgumentParser(
        description='Replace all keys from translation file find in given json-path.')

    add_arguments(parser)
    return parser.parse_args()


def main():

    if 1 < len(sys.argv) and "--nogui" == sys.argv[1]:
        args = parse_arguments()
    else:
        args = interview_arguments()

    project_file = args.project
    project_name = os.path.splitext(os.path.basename(project_file))[0]

    translation_file = args.translation
    translation_name = os.path.splitext(os.path.basename(translation_file))[0]

    basepath = os.path.dirname(project_file)
    result = basepath + "/" + project_name + "-" + translation_name + ".json"

    key_list = args.key_list.split(',')

    mapping = load_json(translation_file)
    data = load_json(project_file)

    print("load mapping {} with {} entries".format(translation_file, len(mapping)))
    print("key list contains {} entries".format(len(key_list)))
    replace_values(data, mapping, key_list)

    save_json(result, data)


if __name__ == "__main__":
    main()
