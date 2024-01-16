#! /bin/sh

while [ $# -gt 0 ]; do
    if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
    fi
    shift
done

PREFIX="${RESOURCE_PREFIX:-eas-app}"
CLUSTER_NAME="${PREFIX}-cluster"
echo "Using ${PREFIX} resources"

update_task_definition(){
    if [ -z "$SERVICE" ]; then
        echo "SERVICE is required."
        exit
    fi;

    echo "=============== GETTING LATEST TASK DEFINITION ==============="
    latest_task_def=$(aws ecs list-task-definitions \
        --status ACTIVE \
        --sort DESC \
        --max-items 1 \
        --family-prefix "${PREFIX}-${SERVICE}" \
        --output json \
    | jq '.taskDefinitionArns[0]' | tr -d '"')

    if [ -z "$latest_task_def" ]; then
        echo "Unable to retrieve the latest task definition."
        exit
    else
        echo "Updating the service with the task definition arn: $latest_task_def."
        echo ""
        echo "=============== UPDATING SERVICE ==============="
        aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "${PREFIX}-${SERVICE}" \
        --task-definition "$latest_task_def" \
        --force-new-deployment
    fi
}

update_task_definition
