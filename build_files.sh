#!/bin/bash

# Install Python dependencies from requirements.txt
pip install -r requirements.txt

# Collect static files for the Django project
python manage.py collectstatic --noinput