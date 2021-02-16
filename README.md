# notifications-govuk-alerts

## Installation

Make sure you have:
- Python 3
- NodeJS (LTS)

1. create a [python virtual
environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)
2. run `pip install -r requirements.txt` to install all the python dependencies
3. run `npm install` to get the NodeJS dependencies

## Building the pages

To build the HTML pages and copy the images and fonts across, run `python build.py`.

To compile any `.scss` files in `./src/assets/stylesheets/` into `.css`, run `npm build`.

## Viewing the pages

To view any built pages, run `python -m HTTP.server` in `./dist`.
