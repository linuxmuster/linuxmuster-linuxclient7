### Setup
Setup development environment for running unit test locally (Tested with Python 3.10):

1. `python3 -m venv ./venv`
2. `. ./venv/bin/activate`
3. `cd ./usr/lib/python3/dist-packages/linuxmusterLinuxclient7`
4. `pip install -r requirements.txt`

To run tests:
1. `pytest`
2. with coverage: `pytest --cov=./ --cov-report=xml`