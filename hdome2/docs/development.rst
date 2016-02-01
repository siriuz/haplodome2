Development Environment
=========
This project is set up to use Django Extensions' shell_plus Jupyter notebook for journaled interactive python development.  
The default Jupyter server configuration listens on 0.0.0.0:8888. This setting can be modified in the ``config/settings/local.py`` file under ``NOTEBOOK_ARGUMENTS``.

Database Setup
==============
1. Create user (username vagrant)::

   > sudo -u postgres createuser --superuser --pwprompt vagrant 

2. Create database (table name vagrant)::

   > createdb vagrant

cookiecutter-django is set up to use django-environ to read configuration settings from environmental variables, thus the environmental variable ``DATABASE_URL`` will be read at Django's start up.::

> export DATABASE_URL=postgres://vagrant:vagrant@localhost:5432/vagrant  

Alternatively put it in a .env file in the django project directory and it will be read by settings.py at django start up.
