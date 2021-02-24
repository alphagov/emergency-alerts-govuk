# notifications-govuk-alerts

## Installation

Make sure you have:
- Python 3
- NodeJS (LTS)

1. create a [python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)
2. run `make bootstrap`

## Building the pages

```
make build
```

## Viewing the pages

```
make run
```

## Running the tests

```
make test
```

## Code linting

### SCSS

SCSS code in this repository is linted according to the [GDS Stylelint Config](https://github.com/alphagov/stylelint-config-gds) before being compiled into CSS.

## Browser support

We aim to match the [browsers supported by GOVUK Frontend](https://github.com/alphagov/govuk-frontend#browser-and-assistive-technology-support) (includes Internet Explorer 8-10).
