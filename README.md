AioNT
=====

An asynchronous way to fetch team and racer statistics from [nitrotype](https://nitrotype.com).

Installation
============
```
pip install aiont
```

Basic Usage:
===========
```python
import asyncio
import aiont


async def main():
    #create a session
    session = aiont.Session()

    #get a Racer object
    racer = await session.get_racer("travis")

    #print races the racer has
    print(racer.races)

    #get a Team object
    team = await session.get_team("NT")

    #print team's daily speed
    print(team.daily_speed)


```