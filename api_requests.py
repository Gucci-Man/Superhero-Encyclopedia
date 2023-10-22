"""Handling requests to API"""

import requests
from secret import API_KEY

class Superhero:
    """Superhero object that contains their info"""

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.aliases = data["biography"]["aliases"]
        self.birth_place = data["biography"]["place-of-birth"]
        self.first_appear = data["biography"]["first-appearance"]
        self.job = data["work"]["occupation"]
        self.image = data["image"]["url"]


def get_request(hero_id):
    """Sends request to API and return superhero object"""

    resp = requests.get(
        f"https://superheroapi.com/api/{API_KEY}/{hero_id}")
    
    data = resp.json()
    return Superhero(data)