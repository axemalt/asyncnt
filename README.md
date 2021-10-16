AioNT
=====

An asynchronous way to fetch team and racer statistics from [nitrotype](https://nitrotype.com).

Installation
============
```
pip install -U aiont
```

Basic Usage:
===========
```python
import asyncio
import aiont


async def main():
    #create a session
    async with aiont.Session() as session:
        #get a Racer object
        racer = await session.get_racer("travis")
        #print races the racer has
        print(racer.races)

        #get a Team object
        team = await session.get_team("NT")
        #print team's daily speed
        print(team.daily_speed)
```
Session Class
=============
Methods:
* `await get_racer(username: str, *, session: Optional[aiohttp.ClientSession] = None) -> Optional[Racer]`: Returns a Racer object from the racer username.
* `await get_team(self, tag: str, *, session: aiohttp.ClientSession = None) -> Optional[Team]`: Returns a Team object from the team tag.

Racer Class
===========
Attribues:
* `user_id`: The racer's user ID.
* `username`: The racer's username.
* `display_name`: The racer's display name.
* `membership`: The racer's membership (premium, basic).
* `level`: The racer's level.
* `experience`: The racer's experience.
* `profile_views`: The racer's profile views.
* `nitros`: The racer's amount of owned nitros.
* `nitros_used`: The racer's amount of used nitros.
* `nitros_total`: The racer's amount of owned nitros and used nitros added together.
* `races`: The racer's race amount.
* `wpm_average`: The racer's average wpm.
* `wpm_high`: The racer's highest wpm.
* `friend_reqs_allowed`: If the racer allows friend requests.
* `looking for team`: If the racer accepts team invites.
* `created`: The racer's account creation date (seconds since unix epoch).
* `car`: The racer's current car.
* `cars`: All of the racer's cars.
* `cars_owned`: The racer's amount of owned cars.
* `cars_sold`: The racer's amount of sold cars.
* `cars_total`: The racer's amount of owned cars and sold cars added together.
* `loot`: The racer's loot.

Methods:
* `await get_team() -> Optional[Team]`: The racer's team.

Team Class
==========
Attribues:
* `daily_races`: The team's daily races.
* `daily_speed`: The team's daily points.
* `daily_accuracy`: The team's daily accuracy.
* `daily_points`: The team's daily points.
* `season_races`: The team's season races.
* `season_speed`: The team's season points.
* `season_accuracy`: The team's season accuracy.
* `season_points`: The team's season points.
* `alltime_races`: The team's all time races.
* `alltime_speed`: The team's all time points.
* `alltime_accuracy`: The team's all time accuracy.
* `alltime_points`: The team's all time points.

Methods:
* `await get_captain() -> Racer`: The team's captain.
* `await get_leaders(*, include_captain: bool = False) -> List[Optional[Racer]]`: The team's leaders.

Lisence
=======
MIT