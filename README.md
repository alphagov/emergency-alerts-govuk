# emergency-alerts-govuk

Website for emergency alerts, hosted under /alerts on GOV.UK.

- [Preview (in GOV.UK Integration)](https://www.integration.publishing.service.gov.uk/alerts) (ask in Slack for credentials)
- [Staging (in GOV.UK Staging)](https://www.staging.publishing.service.gov.uk/alerts) (needs VPN)\*
- [Live (gov.uk/alerts)](https://www.gov.uk/alerts)

\* Note that, even when connected to the VPN, you may see a 403 Forbidden page due to [an issue with the way GOV.UK Fastly is configured with Fastly shielding](https://github.com/alphagov/govuk-cdn-config/pull/362).

## Setting up to run the gov.uk/alerts locally

### Local Development Environment Setup
Ensure that you have first followed all of the local development environment setup steps, that can be found [here](https://gds-ea.atlassian.net/wiki/spaces/EA/pages/3211265/Mac+Setup), before attempting to run the gov.uk/alerts locally.

### Python version

You can find instructions on setting the correct Python version [here](https://gds-ea.atlassian.net/wiki/spaces/EA/pages/192217089/Setting+up+Local+Development+Environment#Setting-Python-Version).

### NodeJS & NPM

If you don't have NodeJS on your system, install it with homebrew.

```shell
brew install node
```

`nvm` is a tool for managing different versions of NodeJS. Follow [the guidance on nvm's github repository](https://github.com/nvm-sh/nvm#installing-and-updating) to install it.

Once installed, run the following to switch to the version of NodeJS for this project. If you don't
have that version, it should tell you how to install it.

```shell
nvm use
```
### Additional Dependencies for Macbook M1 Pro Users
To compile and run the project you need the following

```
brew install proj
brew install geos
```

### Pre-commit

- If `pre-commit` is not already installed on your machine, run
`brew install pre-commit`

- In this repository’s folder, run
`pre-commit install` and
`pre-commit install-hooks`

## To run the application

The instructions to run the gov.uk/alerts server can be found [here](https://gds-ea.atlassian.net/wiki/spaces/EA/pages/192217089/Setting+up+Local+Development+Environment#Run-the-Gov.uk%2FAlerts-Website).

We aim to match the [browsers supported by GOVUK Frontend](https://github.com/alphagov/govuk-frontend#browser-and-assistive-technology-support) (includes Internet Explorer 8-10).

Any Python code changes you make should be picked up automatically in development. If you're developing JavaScript code, run `npm run watch` to achieve the same.

**This app can also be run as a Celery worker, but this is currently broken on some machines. See https://github.com/alphagov/emergency-alerts-govuk/issues/214**

## To test the application

The instructions for running the unit tests for gov.uk/alerts server can be found [here](https://gds-ea.atlassian.net/wiki/spaces/EA/pages/192217089/Setting+up+Local+Development+Environment#Running-the-Unit-Tests).

To continuously run js tests, run `npm run test-watch`.

To run a specific JavaScript test, you'll need to copy the full command from `package.json`.

## Further documentation

- [Architecture](docs/architecture.md)
- [Image optimisation](docs/image-optimisation.md)
- [Setting up redirects](docs/redirects.md)
- [Updating dependencies](https://github.com/alphagov/notifications-manuals/wiki/Dependencies)
- [JavaScript documentation](https://github.com/alphagov/notifications-manuals/wiki/JavaScript-Documentation)
