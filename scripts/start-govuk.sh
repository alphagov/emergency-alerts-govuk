#! /bin/sh

echo "Start script executing for govuk-alerts celery worker..."

function configure_container_role(){
  aws configure set default.region eu-west-2
}

function run_celery(){
  cd $API_DIR;
  . $VENV_API/bin/activate && make run-celery &
}

configure_container_role
run_celery
