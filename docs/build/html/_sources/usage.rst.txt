Usage
=====

Installation
------------

To use AioNT, first install it using pip:

.. code-block:: console

   $ pip install aiont

Getting Data
------------

To retrieve data, you first need to create a :py:class:`aiont.Session` object.
Then, you can use :py:func:`aiont.Session.get_racer` and :py:func:`aiont.Session.get_team` to get a :py:class:`aiont.Racer` object and a :py:class:`aiont.Team` object, respectively.

Example
-------

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