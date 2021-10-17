Usage
=====

Installation
------------

To use AsyncNT, first install it using pip:

.. code-block:: console

   $ pip install asyncnt

Getting Data
------------

To retrieve data, you first need to create a :py:class:`asyncnt.Session` object.
Then, you can use :py:func:`asyncnt.Session.get_racer` and :py:func:`asyncnt.Session.get_team` to get a :py:class:`asyncnt.Racer` object and a :py:class:`asyncnt.Team` object, respectively.

Example
-------

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