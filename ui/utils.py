# Parses request data from json to python dict
def parse_json(data):
    dictionary = {}
    [dictionary.update({key: data.get(key)}) for key in data]
    return dictionary