#!/bin/bash -e

virtualenv /tmp/venv
source /tmp/venv/bin/activate
pip install -r requirements.txt
voila gpx-race2.ipynb
