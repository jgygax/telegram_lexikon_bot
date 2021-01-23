import json
import random


class Lexikon:
    def __init__(self, lexikon_path="Lexikon/finalout.json"):

        with open(lexikon_path) as json_file:
            self.LEXIKON = json.load(json_file)

    
    def get_definition(self):
        return random.choice(list(self.LEXIKON.items()))


