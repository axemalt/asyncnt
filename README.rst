AioNT
=====

An asynchronous way to fetch team and racer statistics from
`nitrotype <https://nitrotype.com>`__.

Installation
============

::

    pip install -U aiont

Basic Usage:
============

.. code:: python

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

Session Class
=============

Methods: 

* ``await get_racer(username: str, *, session: Optional[aiohttp.ClientSession] = None) -> Optional[Racer]``: Get a racer with a username. 
* ``await get_team(self, tag: str, *, session: aiohttp.ClientSession = None) -> Optional[Team]``: Get a team with a tag.

Racer Class
===========

Attribues:

* ``id``: The racer's user ID. 
* ``username``: The racer's username. 
* ``display_name``: The racer's display name. 
* ``membership``: The racer's membership (gold, basic). 
* ``level``: The racer's level. 
* ``experience``: The racer's experience. 
* ``profile_views``: The racer's profile views. 
* ``nitros``: The racer's amount of owned nitros. 
* ``nitros_used``: The racer's amount of used nitros. 
* ``nitros_total``: The racer's amount of owned nitros and used nitros added together. 
* ``races``: The racer's race amount. 
* ``average_speed``: The racer's average wpm. 
* ``high_speed``: The racer's highest wpm. 
* ``friend_reqs_allowed``: If the racer allows friend requests. 
* ``looking for team``: If the racer accepts team invites. 
* ``created``: The racer's account creation date (seconds since unix epoch). 
* ``car``: The racer's current car. 
* ``cars``: All of the racer's cars. 
* ``cars_owned``: The racer's amount of owned cars. 
* ``cars_sold``: The racer's amount of sold cars. 
* ``cars_total``: The racer's amount of owned cars and sold cars added together. 
* ``loot``: The racer's loot.

Methods: 

* ``await get_team() -> Optional[Team]``: Get the racer's team.

Team Class
==========

Attribues: 

* ``id``: The team's ID. 
* ``tag``: The team's tag. 
* ``name``: The team's name. 
* ``open``: If the team allows new members.
* ``created``: The team's creation date (seconds since unix epoch). 
* ``profile_views``: The team's profile views. 
* ``member_count``: The team's member count. 
* ``min_level``: The team's minimum required level. 
* ``min_races``: The team's minimum required races. 
* ``min_speed``: The team's minimum required speed. 
* ``description``: The team's description. 
* ``daily_races``: The team's daily races. 
* ``daily_speed``: The team's daily points. 
* ``daily_accuracy``: The team's daily accuracy. 
* ``daily_points``: The team's daily points. 
* ``season_races``: The team's season races. 
* ``season_speed``: The team's season points. 
* ``season_accuracy``: The team's season accuracy. 
* ``season_points``: The team's season points. 
* ``alltime_races``: The team's all time races. 
* ``alltime_speed``: The team's all time points. 
* ``alltime_accuracy``: The team's all time accuracy. 
* ``alltime_points``: The team's all time points.

Methods: 

* ``await get_captain() -> Racer``: Get the captain of the team. 
* ``await get_leaders(*, include_captain: bool = False) -> List[Optional[Racer]]``: Get the leaders of the team. 
* ``await get_members(*, include_leaders: bool = False) -> List[Optional[Racer]]``: Get the members of the team.

Car Class
=========

Attributes: 

* ``id``: The car's ID. 
* ``hue_angle``: The car's hue angle. 
* ``url``: The car's image url.

Loot Class
==========

Attributes: 

* ``id``: The loot's ID. 
* ``type``: The loot's type. 
* ``name``: The loot's name. 
* ``rarity``: The loot's rarity.

Lisence
=======

MIT
