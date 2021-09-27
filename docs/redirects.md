# Redirects

If you need to set up a new redirect, you can do that in our notifications-broadcasts-infra repository.

In there, head to `terraform/modules/govuk-alerts-website/files/redirects` and add your redirect to REDIRECTS constant, using the following format:

```
REDIRECTS = {"<uri of page you want to redirect from>": "<uri of page you want to redirect to>"}
```

Deploy-wise, you will need to do 3 deploys in quick succession:

1. deploy a PR that adds the page to redirect to
2. deploy the lambda change (through govuk-alerts-infra Concourse pipeline)
3. deploy a PR that removed the old page we want to get rid of
