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


with open(os.path.join(os.path.dirname(__file__), 'scrapers.json')) as f:
    scrapers = json.load(f)["scrapers"]


with open(os.path.join(os.path.dirname(__file__), 'cars.json')) as f:
    data = json.load(f)["cars"]
    cars = {int(id): name for id, name in data.items()}


class AioNT:
    async def get_data(self, *args, **kwargs):
        func = functools.partial(self.requests.get, headers=self.requests.headers, *args, **kwargs)
        raw_data = asyncio.get_event_loop().run_in_executor(None, func)

        regex_result = re.search(
            r"RACER_INFO: \{\"(.*)\}",
            raw_data.text.strip()
        ).group(1)

        data = json.loads(
            '{"'
            + regex_result
            + "}"
        )
        return data

    @classmethod
    async def get_racer(cls, username, scraper=None):
        cls.requests = scraper or jsonpickle.decode(random.choice(scrapers))
        return cls(await cls.get_data(f"https://nitrotype.com/racer/{username}"))
    

class Racer:
    def __init__(self, data, scraper=None):
        if not data:
            return

        #self.team = Team(data.get("tag"))
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
        self.created = date.fromtimestamp(data["createdStamp"]).strftime(
            "%d %B %Y"
        )

        if data["carHueAngle"] == 0:
            self.car = (
                f'https://www.nitrotype.com/cars/{data["carID"]}_large_1.png'
            )
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


class Team:
    def __init__(self, team, scraper=None):
        self.requests = jsonpickle.decode(random.choice(scrapers))
        if scraper:
            self.requests = scraper

        def get(*args, **kwargs):
            return self.requests.get(headers=self.requests.headers, *args, **kwargs)

        try:

            def api_get(path):
                return get(f"https://www.nitrotype.com/api/{path}")

            self.data = json.loads(api_get(f"teams/{team}").content)
            if self.data["success"] == False:
                return

        except Exception:
            self.data = {}

        else:
            self.data = self.data["data"]
            self.info = self.data["info"]

        stats = self.data["stats"]
        for stat in stats:
            if stat["board"] == "daily":
                self.daily_pre = stat
                self.daily_races = self.daily_pre["played"]
                self.daily_speed = (
                    int(self.daily_pre["typed"]) / 5 / self.daily_pre["secs"] * 60
                )
                self.daily_accuracy = 100 - (
                    (int(self.daily_pre["errs"]) / int(self.daily_pre["typed"])) * 100
                )
                self.daily_points = (
                    self.daily_races
                    * (100 + (self.daily_speed / 2))
                    * self.daily_accuracy
                    / 100
                )

            if stat["board"] == "season":
                self.season_pre = stat
                self.season_races = self.season_pre["played"]
                self.season_speed = (
                    int(self.season_pre["typed"]) / 5 / self.season_pre["secs"] * 60
                )
                self.season_accuracy = 100 - (
                    (int(self.season_pre["errs"]) / int(self.season_pre["typed"])) * 100
                )
                self.season_points = (
                    self.season_races
                    * (100 + (self.season_speed / 2))
                    * self.season_accuracy
                    / 100
                )

            if stat["board"] == "alltime":
                self.alltime_pre = stat
                self.alltime_races = self.alltime_pre["played"]
                self.alltime_speed = (
                    int(self.alltime_pre["typed"]) / 5 / self.alltime_pre["secs"] * 60
                )
                self.alltime_accuracy = 100 - (
                    (int(self.alltime_pre["errs"]) / int(self.alltime_pre["typed"]))
                    * 100
                )
                self.alltime_points = (
                    self.alltime_races
                    * (100 + (self.alltime_speed / 2))
                    * self.alltime_accuracy
                    / 100
                )

            self.leaders = []
            self.captain = (self.info["username"], self.info["displayName"])
            for elem in self.data["members"]:
                if elem["role"] == "officer" and elem["username"] != self.captain[0]:
                    self.leaders.append((elem["username"], elem["displayName"]))
