__title__ = "aiont"
__author__ = "axemalt"
__version__ = "0.0.1"

from cloudscraper import CloudScraper
from requests import Response
import jsonpickle
import functools
import asyncio
import random
import re
import json
import os


with open(os.path.join(os.path.dirname(__file__), "scrapers.json")) as f:
    scrapers = json.load(f)["scrapers"]


class Racer:
    def __init__(self, data: dict) -> None:
        if not data:
            return

        self._team_tag: str = data["tag"]

        self.user_id: int = data["userID"]
        self.username: str = data["username"].title()
        self.name: str = data["displayName"] or self.username
        self.membership: str = data["membership"]
        self.level: int = data["level"]
        self.experience: int = data["experience"]
        self.views: int = data["profileViews"]
        self.current_car_id: int = data["carID"]
        self.nitros: int = data["nitros"]
        self.nitros_used: int = data["nitrosUsed"]
        self.nitros_total: int = self.nitros + self.nitros_used
        self.races: int = data["racesPlayed"]
        self.wpm_average: int = data["avgSpeed"]
        self.wpm_high: int = data["highestSpeed"]
        self.friend_reqs_allowed: bool = bool(data["allowFriendRequests"])
        self.looking_for_team: bool = bool(data["lookingForTeam"])
        self.created: int = data["createdStamp"]

        if data["carHueAngle"] == 0:
            self.car_img_url = f'https://www.nitrotype.com/cars/{data["carID"]}_large_1.png'
        else:
            self.car_img_url = f'https://www.nitrotype.com/cars/painted/{data["carID"]}_large_1_{data["carHueAngle"]}.png'

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
    def __init__(self, data: dict) -> None:
        info: dict = data["info"]
        stats: dict = data["stats"]

        self._captain_username: str = info["username"]
        self._leader_usernames: list[str] = [
            member["username"]
            for member in data["members"]
            if member["role"] == "officer"
        ]

        for stat in stats:
            board: str = stat["board"]
            speed: float = int(stat["typed"]) / 5 / stat["secs"] * 60
            accuracy: float = 100 - int(stat["errs"] / int(stat["typed"])) * 100

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

    async def get_leaders(self, *, include_captain=False) -> list:
        coruntines = []

        for username in self._leader_usernames:
            if username == self._captain_username and not include_captain:
                pass
            else:
                coruntines.append(get_racer(username))

        return await asyncio.gather(*coruntines)


async def get_data(scraper: CloudScraper=None, *args, **kwargs)-> Response:
    scraper = scraper or jsonpickle.decode(random.choice(scrapers))
    func = functools.partial(scraper.get, headers=scraper.headers, *args, **kwargs)
    return await asyncio.get_event_loop().run_in_executor(None, func)


async def get_racer(username: str, scraper: CloudScraper=None) -> Racer:
    raw_data: Response = await get_data(scraper, f"https://nitrotype.com/racer/{username}")

    regex_result: str = re.search(r"RACER_INFO: \{\"(.*)\}", raw_data.text.strip()).group(1)

    data: dict = json.loads('{"' + regex_result + "}")

    return Racer(data)


async def get_team(tag: str, scraper: CloudScraper=None) -> Team:
    raw_data: Response = await get_data(scraper, f"https://nitrotype.com/api/teams/{tag}")

    data: dict = json.loads(raw_data.content)

    return Team(data["data"])
