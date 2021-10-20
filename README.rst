AsyncNT
=======

An asynchronous way to fetch data from
`nitrotype <https://nitrotype.com>`_.

Features
========

* Asyncio support
* Access to the Nitro Type API
* Rate limit of 10 requests per second
* Cache to speed up requests

Installation
============

::

    pip install asyncnt

Basic Usage
============

.. code:: python

    import asyncio
    import asyncnt


    async def main():
        #create a session
        async with asyncnt.Session() as session:
            #get a Racer object
            racer = await session.get_racer("travis")
            #print races the racer has
            print(racer.races)

            #get a Team object
            team = await session.get_team("NT")
            #print team's daily speed
            print(team.daily_speed)

Check out the `docs <https://asyncnt.readthedocs.io/en/stable/>`_ for more information.

Lisence
=======

MIT
