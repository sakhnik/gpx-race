#!/bin/bash -e

virtualenv /tmp/venv
source /tmp/venv/bin/activate

pip install -r requirements.txt
