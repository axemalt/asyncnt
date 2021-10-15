__title__ = "aiont"
__author__ = "axemalt"
__version__ = "0.0.1"

from typing import TypeVar, List
import cloudscraper
import asyncio
import aiohttp
import json
import re


TM = TypeVar("TM", bound="Team")
#SN = TypeVar("SN", bound="Session")

class AioNTException(Exception):
    pass


class InvalidRacerUsername(AioNTException):
    def __init__(self):
        message = "The username provided is invalid."
        super().__init__(message)

class InvalidTeamTag(AioNTException):
    def __init__(self):
        message = "The tag provided is invalid."
        super().__init__(message)


class CloudScraper(cloudscraper.CloudScraper):
    def __init__(self):
        super().__init__()

        self.session = aiohttp.ClientSession()

    async def get(self, url: str, *, session: aiohttp.ClientSession = None) -> aiohttp.ClientResponse:
        session = session or self.session

        return await session.get(url, headers=self.headers)

    async def close(self) -> None:
        if not self.session.closed:
            await self.session.close()


class Racer:
    def __init__(self, data: dict, *, scraper) -> None:
        self._scraper = scraper

        self.team_tag: str = data.get("tag")
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
            self.car_img_url = (
                f'https://www.nitrotype.com/cars/{data["carID"]}_large_1.png'
            )
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

    async def get_team(self) -> TM:
        return await self._scraper.get_team(self.team_tag)


class Team:
    def __init__(self, data: dict, *, scraper: S) -> None:
        self._scraper = scraper

        info: dict = data["info"]
        stats: dict = data["stats"]

        self.captain_username: str = info["username"]
        self.leader_usernames: List[str] = [
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

    async def get_captain(self) -> Racer:
        return await self._scraper.get_racer(self.captain_username)

    async def get_leaders(self, *, include_captain=False) -> List[Racer]:
        coruntines = []

        for username in self.leader_usernames:
            if username == self.captain_username and not include_captain:
                pass
            else:
                coruntines.append(self._scraper.get_racer(username))

        return await asyncio.gather(*coruntines)


class Session:
    def __init__(self, *, session=None):
        self._session = session or aiohttp.ClientSession()

    def __del__(self):
        if not self._session.closed:
            loop = asyncio.get_event_loop()
            loop.create_task(self._session.close())

    async def _get(self, url: str, *, session: aiohttp.ClientSession = None) -> aiohttp.ClientResponse:
        session = session or self._session

        return await session.get(url, headers=self.headers)

    async def get_racer(self, username: str, *, session: aiohttp.ClientSession = None) -> Racer:

        raw_data: aiohttp.ClientResponse = await self._get(
            f"https://nitrotype.com/racer/{username}",
            session=session
        )
        text = await raw_data.text()

        regex_result: str = re.search(
            r"RACER_INFO: \{\"(.*)\}", text.strip()
        )
        if regex_result is None:
            raise InvalidRacerUsername

        data = json.loads('{"' + regex_result.group(1) + "}")

        return Racer(data, scraper=self)


    async def get_team(self, tag: str, *, session: aiohttp.ClientSession = None) -> Team:
        raw_data: aiohttp.ClientResponse = await self._get(
            f"https://nitrotype.com/api/teams/{tag}",
            session=session
        )
        data = await raw_data.json()

        if not data["data"].get("info"):
            raise InvalidTeamTag

        return Team(data["data"], scraper=self)
