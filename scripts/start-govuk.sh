#! /bin/sh
timestamp_filename='/eas/emergency-alerts-govuk/celery-beat-healthcheck'
echo "Start script executing for govuk-alerts celery worker..."

function configure_container_role(){
    aws configure set default.region eu-west-2
}

function run_celery(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && make run-celery
}

function flask_publish(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && flask publish-with-assets &
}

function update_timestamp(){
    echo $(date +%s) > $timestamp_filename
    chown easuser:easuser $timestamp_filename
}

if [[ ! -z $DEBUG ]]; then
    echo "Starting in debug mode.."
    while true; do
        echo 'Debug mode active..';
        update_timestamp
        sleep 10;
    done
else
    configure_container_role
    update_timestamp
    flask_publish
    run_celery
fi
