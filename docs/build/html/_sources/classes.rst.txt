Classes
=======

Session Class
-------------

.. autoclass:: asyncnt.Session
    :members:

Racer Class
-----------

.. autoclass:: asyncnt.Racer

    .. autoattribute:: id

    .. autoattribute:: username

    .. autoattribute:: display_name

    .. autoattribute:: title

    .. autoattribute:: url
    
    .. autoattribute:: membership
    
    .. autoattribute:: level
    
    .. autoattribute:: experience
    
    .. autoattribute:: profile_views
    
    .. autoattribute:: nitros
    
    .. autoattribute:: nitros_used
    
    .. autoattribute:: nitros_total
    
    .. autoattribute:: races

    .. autoattribute:: longest_session
    
    .. autoattribute:: team_tag
    
    .. autoattribute:: average_speed
    
    .. autoattribute:: high_speed
    
    .. autoattribute:: friend_reqs_allowed
    
    .. autoattribute:: looking_for_team
    
    .. autoattribute:: created
    
    .. autoattribute:: cars_owned
    
    .. autoattribute:: cars_sold
    
    .. autoattribute:: cars_total

    .. autoproperty:: raw_car

    .. autoproperty:: raw_cars

    .. autoproperty:: raw_loot
    
    .. autoproperty:: raw_team
    
    .. autofunction:: asyncnt.Racer.get_car

    .. autofunction:: asyncnt.Racer.get_cars

    .. autofunction:: asyncnt.Racer.get_loot

    .. autofunction:: asyncnt.Racer.get_team


Team Class
----------

.. autoclass:: asyncnt.Team

    .. autoattribute:: id

    .. autoattribute:: tag

    .. autoattribute:: name

    .. autoattribute:: color

    .. autoattribute:: url

    .. autoattribute:: open

    .. autoattribute:: created

    .. autoattribute:: profile_views

    .. autoattribute:: member_count

    .. autoattribute:: min_level

    .. autoattribute:: min_races

    .. autoattribute:: min_speed

    .. autoattribute:: description

    .. autoattribute:: daily_races

    .. autoattribute:: daily_speed

    .. autoattribute:: daily_accuracy

    .. autoattribute:: daily_points

    .. autoattribute:: season_races

    .. autoattribute:: season_speed

    .. autoattribute:: season_accuracy

    .. autoattribute:: season_points

    .. autoattribute:: all_time_races

    .. autoattribute:: all_time_speed

    .. autoattribute:: all_time_accuracy

    .. autoattribute:: all_time_points

    .. autoproperty:: raw_captain

    .. autoproperty:: raw_leaders

    .. autoproperty:: raw_members

    .. autofunction:: asyncnt.Team.get_captain

    .. autofunction:: asyncnt.Team.get_leaders

    .. autofunction:: asyncnt.Team.get_members

Car Class
---------

.. autoclass:: asyncnt.Car
    :members:

Loot Class
----------

.. autoclass:: asyncnt.Loot
    :members: