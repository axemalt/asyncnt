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
__version__ = "1.6.8"


from typing import Optional, Union, Type, List, Dict
from collections import OrderedDict
from types import TracebackType
import asyncio
import aiohttp
import json
import time
import re


class AsyncNTException(Exception):
    """Base exception class for asyncnt."""

    pass


class InvalidArgument(AsyncNTException):
    """Exception that is raised when an argument provided is invalid."""

    def __init__(self, arg: str, restriction: str) -> None:
        message = f"{arg} must be {restriction}"
        super().__init__(message)


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


class InvalidID(AsyncNTException):
    """Exception that is raised when the ID provided is invalid."""

    def __init__(self) -> None:
        message = "The ID provided is invalid."
        super().__init__(message)


class HTTPException(AsyncNTException):
    """Exception that is raised when an HTTP request operation fails."""

    __slots__ = ["response", "status", "code"]

    def __init__(self, response: aiohttp.ClientResponse):
        self.response = response
        self.status: int = response.status
        self.code: int = 0

        fmt = "{0.status} {0.reason} (error code: {1})"

        super().__init__(fmt.format(self.response, self.code))


class _Cache:
    __slots__ = [
        "cache",
        "maxsize",
        "cache_for",
        "tasks",
    ]

    def __init__(self, cache_for: Union[float, int], maxsize: int = 128) -> None:
        self.cache: OrderedDict[str, aiohttp.ClientResponse] = OrderedDict()
        self.maxsize: int = cache_for
        self.cache_for: float = maxsize
        self.tasks: List[asyncio.Task] = []

    def __del__(self) -> None:
        for task in self.tasks:
            task.cancel()

    def get(self, url: str) -> aiohttp.ClientResponse:
        return self.cache.get(url)

    def clear(self) -> None:
        self.cache = OrderedDict()

    def add(self, url: str, response: aiohttp.ClientResponse) -> None:
        if self.cache_for != 0 and self.maxsize != 0:
            self.cache[url] = response
            task = asyncio.create_task(self.auto_remove(url))
            self.tasks.append(task)

            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def remove(self, url: str) -> None:
        try:
            self.cache.pop(url)
        except KeyError:
            pass

    async def auto_remove(self, url: str):
        await asyncio.sleep(self.cache_for)
        self.remove(url)


class _RateLimit:
    __slots__ = [
        "rate",
        "per",
        "window",
        "tokens",
        "lock",
    ]

    def __init__(self, rate: int = 10, per: Union[float, int] = 1) -> None:
        self.lock = asyncio.Lock()
        self.rate: int = rate
        self.per: float = per
        self.window: float = 0.0
        self.tokens: int = self.rate

    def update(self) -> Optional[float]:
        current = time.time()

        if current > self.window + self.per:
            self.tokens = self.rate
            self.window = current

        if self.tokens == 0:
            return self.per - (current - self.window)

        self.tokens -= 1

    async def wait(self) -> None:
        if self.per != 0:
            async with self.lock:
                wait_for = self.update()
                if wait_for:
                    await asyncio.sleep(wait_for)
                    self.update()


class Car:
    """Represents a Nitro Type car."""

    __slots__ = [
        "id",
        "name",
        "hue_angle",
        "description",
        "rarity",
        "url",
        "price",
        "enter_sound",
    ]

    def __init__(self, data: Dict, hue_angle: Optional[int] = None) -> None:
        options = data["options"]

        #: The car's id.
        self.id: int = data["carID"]
        #: The car's name.
        self.name: str = data["name"]
        #: The car's hue angle.
        self.hue_angle: int = hue_angle or 0
        #: The car's description.
        self.description: Optional[str] = data.get("longDescription")
        #: The car's price.
        self.price: int = data["price"]
        #: The car's enter sound.
        self.enter_sound: str = data["enterSound"]
        #: The car's rarity.
        self.rarity: str = options["rarity"]
        #: The car's image url.
        self.url: str = f"https://nitrotype.com/cars/{options['largeSrc']}"
        if hue_angle is not None:
            src: str = f"{options['largeSrc'][:-4]}_{hue_angle}.png"
            self.url: str = f"https://nitrotype.com/cars/painted/{src}"


class Loot:
    """Represents a Nitro Type loot."""

    __slots__ = ["id", "type", "name", "description", "rarity", "price"]

    def __init__(self, data: Dict) -> None:
        #: The loot's ID.
        self.id: int = data["lootID"]
        #: The loot's type.
        self.type: str = data["type"]
        #: The loot's name.
        self.name: str = data["name"]
        #: The loot's price.
        self.price: Optional[int] = data.get("price")
        #: The loot's rarity.
        self.rarity = None
        if data.get("options") is not None:
            self.rarity: str = data["options"]["rarity"]


class Racer:
    """Represents a Nitro Type racer."""

    __slots__ = [
        "id",
        "username",
        "display_name",
        "title",
        "url",
        "tag_and_name",
        "membership",
        "level",
        "experience",
        "profile_views",
        "nitros",
        "nitros_used",
        "nitros_total",
        "races",
        "longest_session",
        "team_tag",
        "average_speed",
        "high_speed",
        "friend_reqs_allowed",
        "looking_for_team",
        "created",
        "cars_owned",
        "cars_sold",
        "cars_total",
        "_scraper",
        "_car",
        "_cars",
        "_loot",
        "_team",
    ]

    def __init__(self, data: Dict, *, scraper: Session) -> None:
        self._scraper: Session = scraper
        self._car: Dict = {"id": data["carID"], "hue_angle": data["carHueAngle"]}
        self._cars: List[Dict] = []
        self._loot: List[Dict] = []
        self._team: Dict = {
            "id": data.get("teamID"),
            "tag": data.get("tag"),
            "color": data.get("tagColor"),
        }

        #: The racer's user ID.
        self.id: int = data["userID"]
        #: The racer's username.
        self.username: str = data["username"]
        #: The racer's display name.
        self.display_name: str = data["displayName"] or self.username
        #: The racer's current title.
        self.title: str = data["title"]
        #: The racer's profile url.
        self.url: str = f"https://nitrotype.com/racer/{self.username}"
        #: The racer's team tag. ``None`` if the racer has no team.
        self.team_tag: Optional[str] = data.get("tag")
        #: The racer's tag and name. If the racer has no team, this is the same as the display name.
        self.tag_and_name = self.display_name
        if self.team_tag:
            self.tag_and_name = f"[{self.team_tag}] {self.display_name}"

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
        #: The racer's longest session.
        self.longest_session: int = data["longestSession"]

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

        #: The racer's amount of owned cars.
        self.cars_owned: int = 0
        #: The racer's amount of sold cars.
        self.cars_sold: int = 0
        #: The racer's amount of owned and sold cars.
        self.cars_total: int = 0
        for car in data["cars"]:
            if car[1] == "owned":
                raw_car = {"id": car[0], "hue_angle": car[2]}
                self._cars.append(raw_car)
                self.cars_owned += 1
            elif car[1] == "sold":
                self.cars_sold += 1
            self.cars_total += 1

        for loot in data["loot"]:
            raw_loot = {
                "id": loot["lootID"],
                "type": loot["type"],
                "name": loot["name"],
                "rarity": loot["options"]["rarity"],
            }
            self._loot.append(raw_loot)

    @property
    def raw_car(self) -> Dict:
        """The racer's current car. Note that this gives less information than :py:func:`asyncnt.Racer.get_car`."""

        return self._car

    @property
    def raw_cars(self) -> List[Dict]:
        """The racer's cars. Note that this gives less information than :py:func:`asyncnt.Racer.get_cars`."""

        return self._cars

    @property
    def raw_loot(self) -> List[Dict]:
        """The racer's loot. Note that this gives less information than :py:func:`asyncnt.Racer.get_loot`."""

        return self._loot

    @property
    def raw_team(self) -> Dict:
        """The racer's team. Note that this gives less information than :py:func:`asyncnt.Racer.get_team`."""

        return self._team

    async def get_car(self) -> Car:
        """
        Returns the racer's equipped car.

        :raise asyncnt.HTTPException: Getting the car failed.
        :return: The racer's equipped car.
        :rtype: asyncnt.Car
        """

        return await self._scraper.get_car(
            self._car["id"], hue_angle=self._car["hue_angle"]
        )

    async def get_cars(self) -> List[Car]:
        """
        Returns the racer's cars.

        :raise asyncnt.HTTPException: Getting the cars failed.
        :return: The racer's cars.
        :rtype: List[asyncnt.Car]
        """

        return await asyncio.gather(
            *[
                self._scraper.get_car(car["id"], hue_angle=car["hue_angle"])
                for car in self._cars
            ]
        )

    async def get_loot(self) -> List[Loot]:
        """
        Returns the racer's loot.

        :raise asyncnt.HTTPException: Getting the loot failed.
        :return: The racer's loot.
        :rtype: List[asyncnt.Loot]
        """

        return await asyncio.gather(
            *[self._scraper.get_loot(loot["id"]) for loot in self._loot]
        )

    async def get_team(self) -> Optional[Team]:
        """
        Returns the team the racer is on.

        :raise asyncnt.HTTPException: Getting the team failed.
        :return: The racer's team. ``None`` if the racer has no team.
        :rtype: Optional[asyncnt.Team]
        """

        if not self.team_tag:
            return None
        return await self._scraper.get_team(self.team_tag)


class Team:
    """Represents a Nitro Type Team."""

    __slots__ = [
        "id",
        "tag",
        "name",
        "color",
        "url",
        "tag_and_name",
        "open",
        "created",
        "profile_views",
        "member_count",
        "min_level",
        "min_races",
        "min_speed",
        "description",
        "daily_speed",
        "daily_accuracy",
        "daily_points",
        "daily_races",
        "season_speed",
        "season_accuracy",
        "season_points",
        "season_races",
        "all_time_speed",
        "all_time_accuracy",
        "all_time_races",
        "all_time_points",
        "_scraper",
        "_captain",
        "_leaders",
        "_members",
    ]

    def __init__(self, data: Dict, *, scraper: Session) -> None:
        info: Dict = data["info"]
        stats: Dict = data["stats"]

        self._scraper: Session = scraper
        self._captain: Dict = {}
        self._leaders: List[Dict] = []
        self._members: List[Dict] = []

        #: The team's ID.
        self.id: int = info["teamID"]
        #: The team's tag.
        self.tag: str = info["tag"]
        #: The team's name.
        self.name: str = info["name"]
        #: The team's color as a hex.
        self.color: str = info["tagColor"]
        #: The team's profile url.
        self.url: str = f"https://nitrotype.com/racer/{self.tag}"
        #: The team's tag and name.
        self.tag_and_name = f"[{self.tag}] {self.name}"

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

        for member in data["members"]:
            raw_member = {
                "id": member["userID"],
                "username": member["username"],
                "display_name": member["displayName"] or member["username"],
                "membership": member["membership"],
                "races": member["racesPlayed"],
                "raw_car": {"id": member["carID"], "hue_angle": member["carHueAngle"]},
            }
            self._members.append(raw_member)
            if member["role"] == "officer":
                self._leaders.append(raw_member)
            if member["username"] == info["username"]:
                self._captain = raw_member

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

    @property
    def raw_captain(self) -> Dict:
        """The team's captain. Note that this gives less information than :py:func:`asyncnt.Team.get_captain`."""

        return self._captain

    @property
    def raw_leaders(self) -> List[Dict]:
        """The team's leaders. Note that this gives less information than :py:func:`asyncnt.Team.get_leaders`."""

        return self._leaders

    @property
    def raw_members(self) -> List[Dict]:
        """The team's members. Note that this gives less information than :py:func:`asyncnt.Team.get_members`."""

        return self._members

    async def get_captain(self) -> Racer:
        """
        Return the captain of the team.

        :raise asyncnt.HTTPException: Getting the captain failed.
        :return: The team's captain.
        :rtype: asyncnt.Racer
        """

        return await self._scraper.get_racer(self._captain["username"])

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

        for leader in self._leaders:
            if leader["username"] == self._captain["username"] and not include_captain:
                pass
            else:
                coruntines.append(self._scraper.get_racer(leader["username"]))

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

        coruntines: List = []
        leader_usernames: List[str] = [leader["username"] for leader in self._leaders]

        for member in self._members:
            if member["username"] in leader_usernames and not include_leaders:
                pass
            else:
                coruntines.append(self._scraper.get_racer(member["username"]))

        return await asyncio.gather(*coruntines)


class Session:
    """
    First-class interface for making HTTP requests to Nitro Type.

    :param rate: The number of tokens available per :attr:`asyncnt.Session.limit_for` seconds. Defaults to 10.
    :type rate: int
    :param limit_for: The length of the rate limit in seconds. If 0, there is no rate limit. Defaults to 1.
    :type limit_for: Union[float, int]
    :param cache_for: The amount of time in seconds to cache results for. If 0, results will not be cached. Defaults to 300.
    :type cache_for: Union[float, int]
    :param cache_maxsize: The maximum size of the cache. If 0, results will not be cached. Defaults to 128.
    :type cache_maxsize: int
    :raises asyncnt.InvalidArgument: One of the arguments provided is invalid.
    """

    __slots__ = [
        "_loop",
        "_cache",
        "_session",
        "_ratelimit",
    ]

    def __init__(
        self,
        *,
        rate: int = 10,
        limit_for: Union[float, int] = 1,
        cache_for: Union[float, int] = 300,
        cache_maxsize: int = 128,
    ) -> None:

        error_message = "a float or int greater or equal to 0"
        if not isinstance(cache_for, (int, float)):
            raise InvalidArgument("cache_for", error_message)
        if cache_for < 0:
            raise InvalidArgument("cache_for", error_message)

        error_message = "an int greater or equal to 0"
        if not isinstance(cache_maxsize, int):
            raise InvalidArgument("cache_maxsize", error_message)
        if cache_maxsize < 0:
            raise InvalidArgument("cache_maxsize", error_message)

        error_message = "an int greater than 0"
        if not isinstance(rate, int):
            raise InvalidArgument("rate", error_message)
        if rate <= 0:
            raise InvalidArgument("rate", error_message)

        error_message = "a float or int greater or equal to 0"
        if not isinstance(limit_for, (int, float)):
            raise InvalidArgument("limit_for", error_message)
        if limit_for < 0:
            raise InvalidArgument("limit_for", error_message)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
        }

        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._cache: _Cache = _Cache(cache_for, cache_maxsize)
        self._session: aiohttp.ClientSession = aiohttp.ClientSession(headers=headers)
        self._ratelimit: _RateLimit = _RateLimit(rate, limit_for)

    def __del__(self) -> None:
        if not self._session.closed:
            self._loop.create_task(self._session.close())

    async def __aenter__(self) -> Session:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:

        await self._session.close()

    async def get(self, url: str) -> Optional[aiohttp.ClientResponse]:
        """
        Gets data from Nitro Type.

        :param url: The url to get data from.
        :type url: str
        :raise asyncnt.HTTPException: Getting the data failed.
        :return: The data from the url.
        :rtype: Optional[aiohttp.ClientResponse]
        """

        if result := self._cache.get(url):
            return result

        await self._ratelimit.wait()

        response: aiohttp.ClientResponse = await self._session.get(url)

        if response.status == 200:
            self._cache.add(url, response)
            return response
        else:
            raise HTTPException(response)

    async def get_boostrap(self) -> aiohttp.ClientResponse:
        """
        A shortcut to getting data from the bootstrap.

        :raise asyncnt.HTTPException: Getting the data failed.
        :return: The boostrap data.
        :rtype: aiohttp.ClientResponse
        """

        raw_data: aiohttp.ClientResponse = await self.get(
            "https://www.nitrotype.com/index/d8dad03537419610ef21782a075dde2d94c465c61266-1266/bootstrap.js"
        )
        return raw_data

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

    async def get_car(
        self, id: int, *, hue_angle: Optional[int] = None
    ) -> Optional[Car]:

        """
        Get a car with an ID.

        :param id: The car's ID.
        :type id: int
        :param hue_angle: The car's hue angle. Defaults to None.
        :type hue_angle: Optional[int]
        :raise asyncnt.InvalidID: The ID given is invalid.
        :raise asyncnt.InvalidArgument: The hue angle provided is invalid.
        :raise asyncnt.HTTPException: Getting the car failed.
        :return: The car with the given ID.
        :rtype: Optional[asyncnt.Car]
        """

        if hue_angle is not None:
            if not isinstance(hue_angle, int) or hue_angle < 0 or hue_angle % 10 != 0:
                raise InvalidArgument(
                    "hue_angle", "an int factor of 10 between 0 and 350, inclusive"
                )

        raw_data = await self.get_boostrap()
        text = await raw_data.text()

        regex_result: str = re.search(
            r"\"CARS\",(\[.*\])\],\[\"PRODUCTS\"", text
        ).group(1)
        car_data = json.loads('{"cars": ' + regex_result + "}")

        for car in car_data["cars"]:
            if car["carID"] == id:
                return Car(car, hue_angle)

        raise InvalidID

    async def get_loot(self, id: int) -> Optional[Loot]:
        """
        Get loot with an ID.
        :param id: The loot's ID.
        :type id: int
        :raise asyncnt.InvalidLootID: The ID given is invalid.
        :raise asyncnt.HTTPException: Getting the loot failed.
        :return: The loot with the given ID.
        :rtype: Optional[asyncnt.Loot]
        """

        raw_data = await self.get_boostrap()
        text = await raw_data.text()

        regex_result: str = re.search(r"\"LOOT\",(\[.*\])\],\[\"SHOP\"", text).group(1)
        loot_data = json.loads('{"loot": ' + regex_result + "}")

        for loot in loot_data["loot"]:
            if loot["lootID"] == id:
                return Loot(loot)

        raise InvalidID
