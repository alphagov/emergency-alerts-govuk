# Deploying

See [the central documentation about merging and deploying](https://github.com/alphagov/notifications-manuals/wiki/Merging-and-deploying#deployment).

## Caveats

### The [deployment pipeline](https://github.com/alphagov/emergency-alerts-infra/blob/main/ci/govuk-alerts.yml) does't run functional tests for creating / approving alerts.

You should manually test any changes that might affect the way the Celery worker runs or consumes from its queue e.g. changes to environment variables. This can be done locally, by deploying a branch or doing non-continuous (manual) deployment.
