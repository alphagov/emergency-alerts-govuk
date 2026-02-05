#! /bin/sh
timestamp_filename='/eas/emergency-alerts-govuk/celery-beat-healthcheck'
CONTAINER_ID=$(curl -s "$ECS_CONTAINER_METADATA_URI_V4/task" | jq -r ".TaskARN" | cut -d "/" -f 3)
CURRENT_TIMESTAMP=$(date +%s)
echo "Start script executing for govuk-alerts celery worker..."

function configure_container_role(){
    aws configure set default.region ${AWS_REGION}
}

function run_celery(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && make run-celery
}

function flask_publish(){
    cd $DIR_GOVUK;
    . $VENV_GOVUK/bin/activate && opentelemetry-instrument flask publish-with-assets --container-id "$CONTAINER_ID" --current-timestamp "$CURRENT_TIMESTAMP"
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
