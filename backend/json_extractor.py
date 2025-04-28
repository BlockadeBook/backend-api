import json

from app.authors.models import *
from app.notes.models import *
from app.point.models import *

model_classes = [Point, PointSubType, PointSubSubType, PointType, PointCoordinates, Rayon,
                 Author, FamilyStatus, PoliticalParty, Religion, SocialClass, Nationality, Education, Occupation, Card,
                 Note, Diary, Tag, NoteType, Temporality]

model = {}

# json object (int, str, dict, list) -> model
def extract(json_data):
    if type(json_data) is str:
        return json_data
    if type(json_data) is int:
        return json_data
    if type(json_data) is dict:
        res = {}
        for [k, v] in json_data.items():
            if k in model.keys():
                res[k] = model[k](**extract(v))
            else:
                res[k] = v

        return res
    if (type(json_data) is list) or (type(json_data) is tuple):
        return [extract(e) for e in json_data]


#string of json -> model
def parse(data):
    return extract(json.loads(data))


def init():
    global model
    for cl in model_classes:
        model[cl.__name__] = cl


if __name__ == '__main__':
    init()
    #example
    # r = parse('{"PointCoordinates": {"latitude": 10, "longitude":20}}')
    # print(r)
