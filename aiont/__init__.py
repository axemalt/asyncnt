__title__ = "aiont"
__author__ = "axemalt"
__version__ = "0.0.1"

from datetime import date
import cloudscraper
import jsonpickle
import functools
import asyncio
import random
import re
import json
import os


with open(os.path.join(os.path.dirname(__file__), "scrapers.json")) as f:
    scrapers = json.load(f)["scrapers"]


with open(os.path.join(os.path.dirname(__file__), "cars.json")) as f:
    data = json.load(f)["cars"]
    cars = {int(id): name for id, name in data.items()}


async def get_data(requests, *args, **kwargs):
    func = functools.partial(requests.get, headers=requests.headers, *args, **kwargs)
    return await asyncio.get_event_loop().run_in_executor(None, func)


async def get_racer(username, scraper=None):
    requests = scraper or jsonpickle.decode(random.choice(scrapers))
    raw_data = await get_data(requests, f"https://nitrotype.com/racer/{username}")

    regex_result = re.search(r"RACER_INFO: \{\"(.*)\}", raw_data.text.strip()).group(1)

    data = json.loads('{"' + regex_result + "}")

    return Racer(data)


async def get_team(tag, scraper=None):
    requests = scraper or jsonpickle.decode(random.choice(scrapers))
    raw_data = await get_data(requests, f"https://nitrotype.com/api/teams/{tag}")

    data = json.loads(raw_data.content)

    return Team(data["data"])


class Racer:
    def __init__(self, data):
        if not data:
            return

        self._team_tag = data["tag"]

        self.userid = data["userID"]
        self.username = data["username"].title()
        self.name = data["displayName"] or self.username
        self.membership = data["membership"]
        self.level = data["level"]
        self.experience = data["experience"]
        self.views = data["profileViews"]
        self.current_car = cars.get(data["carID"])
        self.carid = data["carID"]
        self.nitros = data["nitros"]
        self.nitros_used = data["nitrosUsed"]
        self.nitros_total = self.nitros + self.nitros_used
        self.nitros = self.nitros
        self.nitros_used = self.nitros_used
        self.nitros_total = self.nitros_total
        self.races = data["racesPlayed"]
        self.wpm_average = data["avgSpeed"]
        self.wpm_high = data["highestSpeed"]
        self.friend_reqs_allowed = bool(data["allowFriendRequests"])
        self.looking_for_team = bool(data["lookingForTeam"])
        self.created = date.fromtimestamp(data["createdStamp"]).strftime("%d %B %Y")

        if data["carHueAngle"] == 0:
            self.car = f'https://www.nitrotype.com/cars/{data["carID"]}_large_1.png'
        else:
            self.car = f'https://www.nitrotype.com/cars/painted/{data["carID"]}_large_1_{data["carHueAngle"]}.png'

        self.cars_owned = 0
        self.cars_sold = 0
        self.cars_total = 0
        self.carIDs = []
        for car in data["cars"]:
            if car[1] == "owned":
                self.carIDs.append(car[0])
                self.cars_owned += 1
            elif car[1] == "sold":
                self.cars_sold += 1
            self.cars_total += 1

    async def get_team(self):
        return await get_team(self._team_tag)


class Team:
    def __init__(self, data):
        info = data["info"]
        stats = data["stats"]

        self._captain_username = info["username"]
        self._leader_usernames = [
            member["username"]
            for member in data["members"]
            if member["role"] == "officer"
        ]

        for stat in stats:
            board = stat["board"]
            speed = int(stat["typed"]) / 5 / stat["secs"] * 60
            accuracy = 100 - int(stat["errs"] / int(stat["typed"])) * 100

            setattr(self, f"{board}_pre", stat)
            setattr(self, f"{board}_races", stat["played"])
            setattr(self, f"{board}_speed", speed)
            setattr(self, f"{board}_accuracy", accuracy)
            setattr(
                self,
                f"{board}_points",
                (stat["played"] * (100 + speed / 2) * accuracy / 100),
            )

    async def get_captain(self):
        return await get_racer(self._captain_username)

    async def get_leaders(self, *, include_captain=False):
        coruntines = []

        for username in self._leader_usernames:
            if username == self._captain_username and not include_captain:
                pass
            else:
                coruntines.append(username)

        return await asyncio.gather(*coruntines)
