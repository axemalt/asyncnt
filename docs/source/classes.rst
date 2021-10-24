Classes
=======

Session Class
-------------

.. autoclass:: asyncnt.Session
    
    .. autoproperty:: rate
    
    .. autoproperty:: limit_for
    
    .. autoproperty:: cache_for

    .. autoproperty:: cache_maxsize

    .. autofunction:: asyncnt.Session.set_rate_limit

    .. autofunction:: asyncnt.Session.set_cache_for

    .. autofunction:: asyncnt.Session.set_cache_maxsize

    .. autofunction:: asyncnt.Session.get

    .. autofunction:: asyncnt.Session.get_racer
    
    .. autofunction:: asyncnt.Session.get_team

Racer Class
-----------

.. autoclass:: asyncnt.Racer

    .. autoattribute:: id

    .. autoattribute:: username

    .. autoattribute:: display_name

    .. autoattribute:: url
    
    .. autoattribute:: membership
    
    .. autoattribute:: level
    
    .. autoattribute:: experience
    
    .. autoattribute:: profile_views
    
    .. autoattribute:: nitros
    
    .. autoattribute:: nitros_used
    
    .. autoattribute:: nitros_total
    
    .. autoattribute:: races
    
    .. autoattribute:: team_tag
    
    .. autoattribute:: average_speed
    
    .. autoattribute:: high_speed
    
    .. autoattribute:: friend_reqs_allowed
    
    .. autoattribute:: looking_for_team
    
    .. autoattribute:: created
    
    .. autoattribute:: car
    
    .. autoattribute:: cars_owned
    
    .. autoattribute:: cars_sold
    
    .. autoattribute:: cars_total
    
    .. autoattribute:: cars
    
    .. autoattribute:: loot

    .. autofunction:: asyncnt.Racer.get_team

Team Class
----------

.. autoclass:: asyncnt.Team

    .. autoattribute:: id

    .. autoattribute:: tag

    .. autoattribute:: name

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