#! /bin/sh

echo "Start script executing for govuk-alerts celery worker..."

function configure_container_role(){
    aws configure set default.region eu-west-2
}

function run_celery(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && make run-celery &
}

function flask_publish(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && flask publish-with-assets
}

if [[ ! -z $DEBUG ]]; then
    echo "Starting in debug mode.."
else
    configure_container_role
    run_celery
    flask_publish
fi