# emergency-alerts-govuk

Website for emergency alerts, hosted under /alerts on GOV.UK.

- [Preview (in GOV.UK Integration)](https://www.integration.publishing.service.gov.uk/alerts) (ask in Slack for credentials)
- [Staging (in GOV.UK Staging)](https://www.staging.publishing.service.gov.uk/alerts) (needs VPN)\*
- [Live (gov.uk/alerts)](https://www.gov.uk/alerts)

\* Note that, even when connected to the VPN, you may see a 403 Forbidden page due to [an issue with the way GOV.UK Fastly is configured with Fastly shielding](https://github.com/alphagov/govuk-cdn-config/pull/362).

## Setting up

### Python version

We run Python 3.9 in production.

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

## To run the application

```shell
# install dependencies, etc.
make bootstrap

# run the web app
make run-flask
```

Then visit [localhost:6017/alerts](http://localhost:6017/alerts).

We aim to match the [browsers supported by GOVUK Frontend](https://github.com/alphagov/govuk-frontend#browser-and-assistive-technology-support) (includes Internet Explorer 8-10).

Any Python code changes you make should be picked up automatically in development. If you're developing JavaScript code, run `npm run watch` to achieve the same.

**This app can also be run as a Celery worker, but this is currently broken on some machines. See https://github.com/alphagov/emergency-alerts-govuk/issues/214**

## To test the application

```
# install dependencies, etc.
make bootstrap

# run all the tests
make test

# continuously run js tests
npm run test-watch
```

To run a specific JavaScript test, you'll need to copy the full command from `package.json`.o run a specific JavaScript test, you'll need to copy the full command from `package.json`.

## Further documentation

- [Architecture](docs/architecture.md)
- [Image optimisation](docs/image-optimisation.md)
- [Setting up redirects](docs/redirects.md)
- [Updating dependencies](https://github.com/alphagov/notifications-manuals/wiki/Dependencies)
- [JavaScript documentation](https://github.com/alphagov/notifications-manuals/wiki/JavaScript-Documentation)
