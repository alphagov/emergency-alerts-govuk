# Architecture

⚠️  The following is about the _intended_ architecture of gov.uk/alerts, which may not (yet) reflect reality.

The overall architecture looks like this:

```
                                     +-------------------------------+
                                     |           data.yaml           |
                                     |                               |
                                     |    (legacy static alerts)     |
                                     +-------------------------------+
                                       |
                                       |
                                       v
+------------------------------+     +-------------------------------+     +--------------------------+
|                              |     |                               |     |        Notify API        |
| static pages (e.g. homepage) |     |     common rendering code     |     |                          |
|                              | --> |                               | <-- | dynamic alerts (from DB) |
+------------------------------+     +-------------------------------+     +--------------------------+
                                       |                                     |
                                       |                                     |
                                       v                                     |
                                     +-------------------------------+       |
                                     |     Celery task (on PaaS)     |       |
                                     |                               |       |
                                     | (also triggered by Concourse) | <-----+
                                     +-------------------------------+
                                       |
                                       |
                                       v
+------------------------------+     +-------------------------------+
|   static assets (JS, CSS)    |     |                               |
|                              |     |           S3 bucket           |
|   (uploaded by Concourse)    | --> |                               |
+------------------------------+     +-------------------------------+
                                       |
                                       |
                                       v
                                     +-------------------------------+
                                     |          CloudFront           |
                                     |                               |
                                     |   (tweaks caching headers)    |
                                     +-------------------------------+
                                       |
                                       |
                                       v
                                     +-------------------------------+
                                     |       GOV.UK Fastly CDN       |
                                     +-------------------------------+
```

This app evolved from a handful of scripts generating output files in a `dist/` directory, which were then uploaded to an S3 bucket as part of a Concourse job. The job was also responsible for purging the Fastly CDN to make changes visible quickly. Originally all the alerts on the site were hard-coded in a `data.yaml` file.

In order to show alerts dynamically, we added a Celery task to replace much of the Concourse job, which now builds and uploads static assets to S3, and deploys this repo as a Celery worker. The Celery task fetches alerts from Notify API as a new data source, and is triggered when the app is deployed and when alerts are published.

- 👉 [GOV.UK Fastly CDN configuration](https://docs.publishing.service.gov.uk/manual/notify-emergency-alerts.html)
- 👉 [Concourse deployment pipeline](https://github.com/alphagov/notifications-broadcasts-infra/blob/main/ci/govuk-alerts.yml)
- 👉 [Terraform for AWS S3, CloudFront, etc.](https://github.com/alphagov/notifications-broadcasts-infra/tree/main/terraform/modules/govuk-alerts-website)

In order to support local development, the repo also functions as a Flask app that renders pages on-the-fly and relies on static assets (JS, CSS) being built locally. We could use the Flask app to serve the live site as well, but this would be less robust than the S3 bucket, given the expected traffic patterns for emergency alerts.

The development architecture looks like this:

```
+-------------------------+
|  common rendering code  |
+-------------------------+
  |
  |
  v
+-------------------------+
|        flask app        |
|                         |
|    (local dev only)     |
+-------------------------+
  ^
  |
  |
+-------------------------+
| static assets (JS, CSS) |
+-------------------------+
```
