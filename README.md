# add environment

conda env create flask_env
conda activate flask_env

# add readme

set FLASK_APP=service.app
set FLASK_ENV=development
flask run --port 8080

# tests

pytest -q --cov=service --cov-report=term-missing:skip-covered --cov-fail-under=95

# app + BDD

honcho start

# terminal

behave

# install

pip install -r requirements.txt
