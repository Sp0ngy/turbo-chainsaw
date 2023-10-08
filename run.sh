#!/bin/bash
echo "> Run all django migrations to update database"
python ./manage.py migrate
echo "> Show migrations"
python ./manage.py showmigrations
echo "> Run the django server"
python ./manage.py runserver 0.0.0.0:8000