"""
loads authors, notes, and points from files and ads to database
"""
import argparse
import json
import textwrap
from json import JSONDecodeError

import requests

DATABASE_API = "http://127.0.0.1:8080/"
POST_URLS = {"authors": "authors", "notes":"notes", "points":"points", "tags":"notes/tags"}
DESCRIPTION = """\
helps automatically load data from file and add it to database
currently can add authors, notes, and points

input file must be a json file and have following structure:
{
'authors' : <[list of jsons describing authors]>,
'notes' : <[list of jsons describing notes]>, 
'points' : <[list of jsons describing points]> 
} 

any of these keys can be absent

to see examples of jsons describing authors, notes, and points call 
loader.py --examples 
"""
EXAMPLES = """\
example of json describing author:
{
  "last_name": "string",
  "first_name": "string",
  "middle_name": "string",
  "sex": "M",
  "birth_date": "2025-05-08",
  "biography": "string",
  "has_children": true,
  "family_status_id": 0,
  "social_class_ids": [
    0
  ],
  "nationality_ids": [
    0
  ],
  "religion_ids": [
    0
  ],
  "education_ids": [
    0
  ],
  "occupation_ids": [
    0
  ],
  "political_party_ids": [
    0
  ],
  "card_ids": [
    0
  ],
  "diary_started_at": "2025-05-08",
  "diary_finished_at": "2025-05-08",
  "diary_source": "string"
}

example of json describing note:   
{
  "author_id": 0,
  "note_type_id": 0,
  "temporality_id": 0,
  "created_at": "2025-05-08",
  "citation": "string",
  "source": "string",
  "tag_ids": [
    0
  ],
  "note_to_points": [
    {
      "point_id": 0,
      "description": "string"
    }
  ]
}

example of json describing point:   
{
  "rayon_id": 0,
  "street": "string",
  "building": "string",
  "latitude": 0,
  "longitude": 0,
  "point_type_id": 0,
  "point_subtype_id": 0,
  "point_subsubtype_id": 0,
  "name": "string",
  "description": "string"
}

example of json describing tag:
{
  "name": "string"
}
"""

def load_json(data, logger):
    """
    loads given json into database see structure of json above or via loader.py --help

    :param data: json to load
    :param logger: function which is called to print log messages
    :return: number of successfully loaded objects
    """

    if type(data) is not dict:
        logger("incorrect json structure")
        return 0
    done = 0
    success = 0
    for k, v in data.items():
        logger(f"processing {k}")
        if k not in POST_URLS.keys():
            logger(f"'{k}' is not a valid type of data")
            logger(f"available data types: {POST_URLS.keys()}\n")
            continue
        if type(v) is not list:
            logger(f"{k} must be list\n")
            continue
        for data in v:
            res = requests.post(DATABASE_API + POST_URLS[k], json=data)
            done += 1
            if res.status_code != 200:
                logger(f"failed to post {k}")
                try:
                    logger(res.status_code)
                    logger(json.dumps(json.loads(res.text), sort_keys=True, indent=2, separators=(',', ': ')))
                except JSONDecodeError:
                    logger(res.status_code)
                    logger(res.text)
            else:
                success += 1
                logger(f"post {k} successfully")
    logger(f"successful processed {success}\nfailed {done - success}")
    return success

def no_log(msg):
    pass

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.description = textwrap.dedent(DESCRIPTION)
    parser.add_argument("input_file", type=str, nargs="?", help="file containing authors, notes, and points")
    parser.add_argument("--examples", action="store_true", help="print examples of storing data")
    parser.add_argument("-s", "--silent", action="store_true", help="disable verbose output")
    args = parser.parse_args()
    if args.examples:
        print(EXAMPLES)
        return
    if args.input_file is None:
        print("input file must be specified")
        print("see --help")
        return
    try:
        with open(args.input_file) as fin:
            try:
                data = json.loads(fin.read())
            except json.decoder.JSONDecodeError as e:
                print("data must be a valid json")
                print(e)
                return
            res = load_json(data, no_log if args.silent else print)
            if args.silent:
                print(f"successfully loaded {res}")
    except IOError as e:
        print(f"failed to read {args.input_file}")
        print(e)

if __name__ == "__main__":
    main()