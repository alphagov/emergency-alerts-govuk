# notifications-govuk-alerts

Website for emergency alerts, hosted under /alerts on GOV.UK.

- [Preview (in GOV.UK Integration)](https://www.integration.publishing.service.gov.uk/alerts) (ask in Slack for credentials)
- [Staging (in GOV.UK Staging)](https://www.staging.publishing.service.gov.uk/alerts) (needs VPN)\*
- [Live (gov.uk/alerts)](https://www.gov.uk/alerts)

\* Note that, even when connected to the VPN, you may see a 403 Forbidden page due to [an issue with the way GOV.UK Fastly is configured with Fastly shielding](https://github.com/alphagov/govuk-cdn-config/pull/362).

## Setting up

### Python version

We run Python 3.9 in production.

### NPM packages

```shell
brew install node
```

[NPM](npmjs.org) is Node's package management tool. `n` is a tool for managing different versions of Node. The following installs `n` and uses the long term support (LTS) version of Node.

```shell
npm install -g n
n lts
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

**This app can also be run as a Celery worker, but this is currently broken on some machines. See https://github.com/alphagov/notifications-govuk-alerts/issues/214**

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
