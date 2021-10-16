"""
MIT License

Copyright (c) 2021 axemalt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations


__title__ = "aiont"
__author__ = "axemalt"
__version__ = "0.0.1"


from typing import Optional, Type, List, Dict
from types import TracebackType
import cloudscraper
import asyncio
import aiohttp
import json
import re


class AioNTException(Exception):
    """Base exception class for aiont."""

    pass


class InvalidRacerUsername(AioNTException):
    """Exception that is raised when the racer username provided is invalid."""

    def __init__(self) -> None:
        message = "The username provided is invalid."
        super().__init__(message)


class InvalidTeamTag(AioNTException):
    """Exception that is raised when the team tag provided is invalid."""
    
    def __init__(self) -> None:
        message = "The tag provided is invalid."
        super().__init__(message)


class HTTPException(AioNTException):
    """Exception that is raised when an HTTP request operation fails."""

    def __init__(self, response: aiohttp.ClientResponse):
        self.response = response
        self.status: int = response.status
        self.code: int
        self.code = 0

        fmt = "{0.status} {0.reason} (error code: {1})"

        super().__init__(fmt.format(self.response, self.code))


class Forbidden(HTTPException):
    """Exception that is raised for when status code 403 occurs."""

    pass


class NotFound(HTTPException):
    """Exception that is raised for when status code 404 occurs."""

    pass


class Car:
    """Represents a Nitro Type car."""

    def __init__(self, data):
        self.id = data[0]
        self.owned = data[1] == "owned"
        self.hue_angle = data[2]

        if self.hue_angle == 0:
            self.url = f"https://www.nitrotype.com/cars/{self.id}_large_1.png"
        else:
            self.url = f"https://www.nitrotype.com/cars/painted/{self.id}_large_1_{self.hue_angle}.png"


class Loot:
    """Represents a Nitro Type loot."""

    def __init__(self, data):
        self.id = data["lootID"]
        self.type = data["type"]
        self.name = data["name"]
        self.rarity = data["options"]["rarity"]


class Racer:
    """Represents a Nitro Type racer."""

    def __init__(self, data: Dict, *, scraper: Session) -> None:
        self._scraper = scraper

        self.user_id: int = data["userID"]
        self.username: str = data["username"]
        self.name: str = data["displayName"] or self.username

        self.membership: str = data["membership"]
        self.level: int = data["level"]
        self.experience: int = data["experience"]
        self.profile_views: int = data["profileViews"]

        self.nitros: int = data["nitros"]
        self.nitros_used: int = data["nitrosUsed"]
        self.nitros_total: int = self.nitros + self.nitros_used

        self.races: int = data["racesPlayed"]

        self.wpm_average: int = data["avgSpeed"]
        self.wpm_high: int = data["highestSpeed"]

        self.friend_reqs_allowed: bool = bool(data["allowFriendRequests"])
        self.looking_for_team: bool = bool(data["lookingForTeam"])

        self.created: int = data["createdStamp"]

        self.car: Car = Car([data["carID"], "owned", data["carHueAngle"]])

        self.cars_owned = 0
        self.cars_sold = 0
        self.cars_total = 0
        self.cars: List[Car] = []
        for car in data["cars"]:
            if car[1] == "owned":
                self.cars.append(Car(car))
                self.cars_owned += 1
            elif car[1] == "sold":
                self.cars_sold += 1
            self.cars_total += 1

        self.loot: List[Loot] = []
        for loot in data["loot"]:
            self.loot.append(Loot(loot))

    async def get_team(self) -> Team:
        """Returns the team of the racer as a Team object."""

        return await self._scraper.get_team(self.team_tag)


class Team:
    """Represents a Nitro Type Team"""

    def __init__(self, data: Dict, *, scraper: Session) -> None:
        self._scraper = scraper

        info: Dict = data["info"]
        stats: Dict = data["stats"]

        self._captain_username: str = info["username"]
        self._leader_usernames: List[str] = [
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
        """Returns the captain of the team as a Racer object."""

        return await self._scraper.get_racer(self.captain_username)

    async def get_leaders(self, *, include_captain=False) -> List[Racer]:
        """Returns the leaders of the team as a list of Racer objects."""

        coruntines = []

        for username in self.leader_usernames:
            if username == self.captain_username and not include_captain:
                pass
            else:
                coruntines.append(self._scraper.get_racer(username))

        return await asyncio.gather(*coruntines)


class Session(cloudscraper.CloudScraper):
    """First-class interface for making HTTP requests to Nitro Type."""

    __slots__ = ["_session", "headers"]

    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        super().__init__()

        self._session = session or aiohttp.ClientSession()

    def __del__(self) -> None:
        if not self._session.closed:
            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            loop.create_task(self._session.close())

    async def __aenter__(self) -> Session:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:

        await self._session.close()

    async def _get(
        self, url: str, *, session: Optional[aiohttp.ClientSession] = None
    ) -> aiohttp.ClientResponse:

        session = session or self._session
        response: aiohttp.ClientResponse = await session.get(url, headers=self.headers)

        if response.status == 200:
            return response
        elif response.status == 403:
            raise Forbidden(response)
        elif response.status == 404:
            raise NotFound(response)
        else:
            raise HTTPException(response)

    async def get_racer(
        self, username: str, *, session: Optional[aiohttp.ClientSession] = None
    ) -> Racer:
        """Returns a Racer object from the racer username."""

        raw_data: aiohttp.ClientResponse = await self._get(
            f"https://nitrotype.com/racer/{username}", session=session
        )
        text: str = await raw_data.text()

        regex_result: str = re.search(r"RACER_INFO: \{\"(.*)\}", text.strip())
        if regex_result is None:
            raise InvalidRacerUsername

        data: Dict = json.loads('{"' + regex_result.group(1) + "}")

        return Racer(data, scraper=self)

    async def get_team(
        self, tag: str, *, session: aiohttp.ClientSession = None
    ) -> Team:
        """Returns a Team object from the team tag."""

        raw_data: aiohttp.ClientResponse = await self._get(
            f"https://nitrotype.com/api/teams/{tag}", session=session
        )
        data: Dict = await raw_data.json()

        if not data["data"].get("info"):
            raise InvalidTeamTag

        return Team(data["data"], scraper=self)
