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


__title__ = "asyncnt"
__author__ = "axemalt"
__version__ = "1.2.1"


from typing import Optional, Type, List, Dict
from types import TracebackType
import cloudscraper
import asyncio
import aiohttp
import json
import time
import re


class AsyncNTException(Exception):
    """Base exception class for asyncnt."""

    pass


class InvalidRacerUsername(AsyncNTException):
    """Exception that is raised when the racer username provided is invalid."""

    def __init__(self) -> None:
        message = "The username provided is invalid."
        super().__init__(message)


class InvalidTeamTag(AsyncNTException):
    """Exception that is raised when the team tag provided is invalid."""

    def __init__(self) -> None:
        message = "The tag provided is invalid."
        super().__init__(message)


class HTTPException(AsyncNTException):
    """Exception that is raised when an HTTP request operation fails."""

    def __init__(self, response: aiohttp.ClientResponse):
        self.response = response
        self.status: int = response.status
        self.code: int
        self.code = 0

        fmt = "{0.status} {0.reason} (error code: {1})"

        super().__init__(fmt.format(self.response, self.code))


class Car:
    """Represents a Nitro Type car."""

    def __init__(self, data):
        #: The car's id.
        self.id: int = data[0]
        #: The car's hue angle.
        self.hue_angle: int = data[2]
        #: The car's image url.
        self.url: str = ""

        if self.hue_angle == 0:
            self.url = f"https://www.nitrotype.com/cars/{self.id}_large_1.png"
        else:
            self.url = f"https://www.nitrotype.com/cars/painted/{self.id}_large_1_{self.hue_angle}.png"


class Loot:
    """Represents a Nitro Type loot."""

    def __init__(self, data):
        #: The loot's ID.
        self.id: int = data["lootID"]
        #: The loot's type.
        self.type: str = data["type"]
        #: The loot's name.
        self.name: str = data["name"]
        #: The loot's rarity.
        self.rarity: str = data["options"]["rarity"]


class Racer:
    """Represents a Nitro Type racer."""

    def __init__(self, data: Dict, *, scraper: Session) -> None:
        self._scraper = scraper

        #: The racer's user ID.
        self.id: int = data["userID"]
        #: The racer's username.
        self.username: str = data["username"]
        #: The racer's display name.
        self.display_name: str = data["displayName"] or self.username

        #: The racer's membership (gold, basic).
        self.membership: str = data["membership"]
        #: The racer's level.
        self.level: int = data["level"]
        #: The racer's amount of experience.
        self.experience: int = data["experience"]
        #: The racer's amount of profile views.
        self.profile_views: int = data["profileViews"]

        #: The racer's amount of owned nitros.
        self.nitros: int = data["nitros"]
        #: The racer's amount of used nitros.
        self.nitros_used: int = data["nitrosUsed"]
        #: The racer's amount of owned and used nitros.
        self.nitros_total: int = self.nitros + self.nitros_used

        #: The racer's amount of races.
        self.races: int = data["racesPlayed"]

        #: The racer's team tag. ``None`` if the racer has no team.
        self.team_tag: Optional[str] = data["tag"]

        #: The racer's average speed.
        self.average_speed: int = data["avgSpeed"]
        #: The racer's highest speed.
        self.high_speed: int = data["highestSpeed"]

        #: Whether the racer allows friend requests.
        self.friend_reqs_allowed: bool = bool(data["allowFriendRequests"])
        #: Whether the racer allows team invites.
        self.looking_for_team: bool = bool(data["lookingForTeam"])

        #: The racer's creation time.
        self.created: int = data["createdStamp"]

        #: The racer's current car.
        self.car: Car = Car([data["carID"], "owned", data["carHueAngle"]])

        #: The racer's amount of owned cars.
        self.cars_owned: int = 0
        #: The racer's amount of sold cars.
        self.cars_sold: int = 0
        #: The racer's amount of owned and sold cars.
        self.cars_total: int = 0
        #: The racer's cars.
        self.cars: List[Car] = []
        for car in data["cars"]:
            if car[1] == "owned":
                self.cars.append(Car(car))
                self.cars_owned += 1
            elif car[1] == "sold":
                self.cars_sold += 1
            self.cars_total += 1

        #: The racer's loot.
        self.loot: List[Optional[Loot]] = []
        for loot in data["loot"]:
            self.loot.append(Loot(loot))

    async def get_team(self) -> Optional[Team]:
        """
        Return the team the racer is on.

        :raise asyncnt.HTTPException: Getting the team failed.
        :return: The racer's team. ``None`` if the racer has no team.
        :rtype: Optional[asyncnt.Team]
        """

        if not self.team_tag:
            return None
        return await self._scraper.get_team(self.team_tag)


class Team:
    """Represents a Nitro Type Team."""

    def __init__(self, data: Dict, *, scraper: Session) -> None:
        self._scraper = scraper

        info: Dict = data["info"]
        stats: Dict = data["stats"]

        #: The team's ID.
        self.id: int = info["teamID"]
        #: The team's tag.
        self.tag: str = info["tag"]
        #: The team's name.
        self.name: str = info["name"]

        #: Whether the team allows new members.
        self.open: bool = info["enrollment"] == "open"

        #: The team's creation time.
        self.created: int = info["createdStamp"]
        #: The team's amount of profile views.
        self.profile_views: int = info["profileViews"]
        #: The team's amount of members.
        self.member_count: int = info["members"]

        #: The team's minimum level required to join.
        self.min_level: int = info["minLevel"]
        #: The team's minimum amount of races required to join.
        self.min_races: int = info["minRaces"]
        #: The team's minimum speed required to join.
        self.min_speed: int = info["minSpeed"]

        #: The team's description.
        self.description: str = info["otherRequirements"]

        self._captain_username: str = info["username"]
        self._leader_usernames: List[str] = []
        self._member_usernames: List[str] = []
        for member in data["members"]:
            self._member_usernames.append(member["username"])
            if member["role"] == "officer":
                self._leader_usernames.append(member["username"])

        for stat in stats:
            board: str = stat["board"]
            races: int = stat["played"]
            speed: float = int(stat["typed"]) / 5 / stat["secs"] * 60
            accuracy: float = 100 - int(stat["errs"] / int(stat["typed"])) * 100

            if board == "daily":
                #: The team's daily races.
                self.daily_races: int = races
                #: The team's daily speed.
                self.daily_speed: int = speed
                #: The team's daily accuracy.
                self.daily_accuracy: float = accuracy
                #: The team's daily points.
                self.daily_points: float = races * (100 + speed / 2) * accuracy / 100
            elif board == "season":
                #: The team's season races.
                self.season_races: int = races
                #: The team's season speed.
                self.season_speed: int = speed
                #: The team's season accuracy.
                self.season_accuracy: float = accuracy
                #: The team's season points.
                self.season_points: float = races * (100 + speed / 2) * accuracy / 100
            else:
                #: The team's all time races.
                self.all_time_races: int = races
                #: The team's all time speed.
                self.all_time_speed: int = speed
                #:  The team's all time accuracy.
                self.all_time_accuracy: float = accuracy
                #: The team's all time points.
                self.all_time_points: float = races * (100 + speed / 2) * accuracy / 100

    async def get_captain(self) -> Racer:
        """
        Return the captain of the team.

        :raise asyncnt.HTTPException: Getting the captain failed.
        :return: The team's captain.
        :rtype: asyncnt.Racer
        """

        return await self._scraper.get_racer(self._captain_username)

    async def get_leaders(
        self, *, include_captain: bool = False
    ) -> List[Optional[Racer]]:

        """
        Get the leaders of the team.

        :param include_captain: If the captain should be included. Defaults to ``False``.
        :type include_captain: bool
        :raise asyncnt.HTTPException: Getting the leaders failed.
        :return: The team's leaders.
        :rtype: List[Optional[asyncnt.Racer]]
        """

        coruntines = []

        for username in self._leader_usernames:
            if username == self._captain_username and not include_captain:
                pass
            else:
                coruntines.append(self._scraper.get_racer(username))

        return await asyncio.gather(*coruntines)

    async def get_members(
        self, *, include_leaders: bool = False
    ) -> List[Optional[Racer]]:

        """
        Get the members of the team.

        :param include_leaders: If the captain should be included. Defaults to ``False``.
        :type include_leaders: bool
        :raise asyncnt.HTTPException: Getting the members failed.
        :return: The team's members.
        :rtype: List[Optional[asyncnt.Racer]]
        """

        coruntines = []

        for username in self._member_usernames:
            if username in self._leader_usernames and not include_leaders:
                pass
            else:
                coruntines.append(self._scraper.get_racer(username))

        return await asyncio.gather(*coruntines)


class Session(cloudscraper.CloudScraper):
    """First-class interface for making HTTP requests to Nitro Type."""

    __slots__ = ["_session", "headers"]

    def __init__(self) -> None:
        super().__init__()

        self.per: float = 1
        self.rate: int = 10
        self._lock: asyncio.Lock = asyncio.Lock()
        self._window: float = 0.0
        self._tokens: int = self.rate
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(value=self.rate)

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

    def _update_rate_limit(self) -> Optional[float]:
        current = time.time()

        if current > self._window + self.per:
            self._tokens = self.rate
            self._window = current

        if self._tokens == 0:
            return self.per - (current - self._window)

        self._tokens -= 1

    async def get(self, url: str) -> Optional[aiohttp.ClientResponse]:
        """
        Gets data from Nitro Type.

        :param url: The url to get data from.
        :type url: str
        :raise asyncnt.HTTPException: Getting the data failed.
        :return: The data from the url.
        :rtype: Optional[aiohttp.ClientResponse]
        """

        async with self._lock:
            wait_for = self._update_rate_limit()
            if wait_for:
                await asyncio.sleep(wait_for)
                self._update_rate_limit()
        
        async with self._semaphore:
            response: aiohttp.ClientResponse = await self._session.get(
                url, headers=self.headers
            )

        if response.status == 200:
            return response
        else:
            raise HTTPException(response)


    async def get_racer(self, username: str) -> Optional[Racer]:
        """
        Get a racer with a username.

        :param username: The racer's username.
        :type username: str
        :raise asyncnt.InvalidRacerUsername: The username given is invalid.
        :raise asyncnt.HTTPException: Getting the racer failed.
        :return: The racer with the given username.
        :rtype: Optional[asyncnt.Racer]
        """

        raw_data: aiohttp.ClientResponse = await self.get(
            f"https://nitrotype.com/racer/{username}/"
        )
        text: str = await raw_data.text()

        regex_result: str = re.search(r"RACER_INFO: \{\"(.*)\}", text.strip())
        if regex_result is None:
            raise InvalidRacerUsername

        data: Dict = json.loads('{"' + regex_result.group(1) + "}")

        return Racer(data, scraper=self)

    async def get_team(self, tag: str) -> Optional[Team]:
        """
        Get a team with a tag.

        :param tag: The team's tag.
        :type tag: str
        :raise asyncnt.InvalidTeamTag: The tag given is invalid.
        :raise asyncnt.HTTPException: Getting the team failed.
        :return: The team with the given tag.
        :rtype: Optional[asyncnt.Team]
        """

        raw_data: aiohttp.ClientResponse = await self.get(
            f"https://nitrotype.com/api/teams/{tag}/"
        )
        data: Dict = await raw_data.json()

        if not data["data"].get("info"):
            raise InvalidTeamTag

        return Team(data["data"], scraper=self)
