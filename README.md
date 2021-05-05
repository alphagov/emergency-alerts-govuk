# notifications-govuk-alerts

## Installation

Make sure you have:
- Python 3
- NodeJS (LTS)

1. create a [python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)
2. run `make bootstrap-ci`

For any further updates to dependencies, use `make bootstrap` for step 2.

## Building the pages

```
make build
```

## Viewing the pages

```
make run
```

Then visit [localhost:8000/alerts](http://localhost:8000/alerts).

## Running the tests

```
make test
```

## Code linting

### SCSS

SCSS code in this repository is linted according to the [GDS Stylelint Config](https://github.com/alphagov/stylelint-config-gds) before being compiled into CSS.

## Browser support

We aim to match the [browsers supported by GOVUK Frontend](https://github.com/alphagov/govuk-frontend#browser-and-assistive-technology-support) (includes Internet Explorer 8-10).

## Image optimisation

All image optimisation should be done manually to remove the need for various libraries in our build
environments.

### Inline SVGs

Inline SVGs should be optimised using https://jakearchibald.github.io/svgomg/

### Raster images

Raster images should be optimised using the following tools:
- https://squoosh.app for converting to `.webp` and optimising the result
- https://tinypng.com/ for optimising `.png` files

## Updating dependencies

### Node modules

Updates to Node modules should put any resulting changes to `package-lock.json` into a separate
commit. This makes it easier to merge any differences, if any arise.

For example:

https://github.com/alphagov/notifications-govuk-alerts/pull/23/commits/cc6dc62db58993169461d6b9c6a18d37bfef90a5
