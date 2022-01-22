#!/bin/bash -e

virtualenv /tmp/venv
/tmp/venv/bin/activate

pip install -r requirements.txt

jupyter labextension install @jupyter-widgets/jupyterlab-manager
