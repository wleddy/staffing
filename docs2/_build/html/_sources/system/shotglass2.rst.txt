===============
Shotglass2 Docs
===============

**Shotglass2** is a python package that provides the basic functionality for web sites that are built upon it.

Shotglass
----------------

The **shotglass** module provides a lot of basic functionality.

.. automodule:: shotglass2.shotglass
    :members:

Access Control
-------------------

Access Administration
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: shotglass2.users.admin
    :members:
    

User Login
^^^^^^^^^^^^^

.. automodule:: shotglass2.users.views.login
    :members:
    
Password Processing
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: shotglass2.users.views.password
    :members:
    


Data Storage
---------------

Database
^^^^^^^^^

    The **Database** Class provides the basic connection to a SQLite3 database. 

    The **SqliteTable** Class is used to interact with the records in the tables. Database queries using instances of this class generally return
    a list of `namedlist` objects or `None` if no records are found.


.. automodule:: shotglass2.takeabeltof.database
    :members:
    
Tables
^^^^^^^^^^^^^^^^

Here are a few tables that define the `Users <#shotglass2.users.models.User>`_, 
`Prefs <#shotglass2.users.models.Pref>`_ and `Roles <#shotglass2.users.models.Role>`_ 
that are core to the Shotglass module.

.. automodule:: shotglass2.users.models
    :members:
    
    
Views
-------
    
User
^^^^^^^^

.. automodule:: shotglass2.users.views.user
    :members:
    
.. Role
.. ^^^^^^^^^
.. 
.. .. automodule:: shotglass2.users.views.role
..     :members:
    

Pref
^^^^^^^^^^^^^^
    
.. automodule:: shotglass2.users.views.pref
    :members:
    
Utilities
----------

Date Utilities
^^^^^^^^^^^^^^^^

.. automodule:: shotglass2.takeabeltof.date_utils
    :members:
    
Jinja2 Template Filters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: shotglass2.takeabeltof.jinja_filters
    :members:
    
Mailer
^^^^^^^^^^^

The **mailer** module provides email functions.

.. automodule:: shotglass2.takeabeltof.mailer
    :members:
