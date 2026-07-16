#! /bin/sh
timestamp_filename='/eas/emergency-alerts-govuk/celery-beat-healthcheck'
echo "Start script executing for govuk-alerts"

function configure_container_role(){
    aws configure set default.region ${AWS_REGION:-eu-west-2}
}

PYTHON_COMMAND="python -m"
if [[ ! -z $DEBUGPY_PORT ]]; then
    echo "Starting with debugpy on port $DEBUGPY_PORT"
    PYTHON_COMMAND="python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:${DEBUGPY_PORT} -m"
fi

function run_dramatiq(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && exec $PYTHON_COMMAND dramatiq --skip-logging --processes 1 --threads 2 app.dramatiq_broker:broker
}

function flask_publish(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && $PYTHON_COMMAND flask publish-with-assets --startup
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
    run_dramatiq
fi
