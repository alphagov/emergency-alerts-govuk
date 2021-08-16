# notifications-govuk-alerts

Static AWS S3 website for Emergency Alerts:

- [Preview (in GOV.UK Integration)](https://www.integration.publishing.service.gov.uk/alerts)
- [Live (gov.uk/alerts)](https://www.gov.uk/alerts)

Note that [GOV.UK Staging](https://www.staging.publishing.service.gov.uk/alerts) also points at the Preview version, but this doesn't seem to work reliably.

## Setting up

### Python version

At the moment we run Python 3.6 in production.

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

Then visit [localhost:5000/alerts](http://localhost:5000/alerts).

We aim to match the [browsers supported by GOVUK Frontend](https://github.com/alphagov/govuk-frontend#browser-and-assistive-technology-support) (includes Internet Explorer 8-10).

Any Python code changes you make should be picked up automatically in development. If you're developing JavaScript code, run `npm run watch` to achieve the same.

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

- [Image optimisation](docs/image-optimisation.md)
- [GOV.UK Fastly CDN configuration](https://docs.publishing.service.gov.uk/manual/notify-emergency-alerts.html)
- [Terraform for AWS S3, CloudFront, etc.](https://github.com/alphagov/notifications-broadcasts-infra/tree/main/terraform/modules/govuk-alerts-website)
