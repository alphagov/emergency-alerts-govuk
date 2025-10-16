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
IMAGE_COMMIT_TAG=$REPOSITORY_URI:commit_$COMMIT_ID

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
        exit 1
    else
        echo "=============== UPDATING LATEST TASK DEFINITION ==============="

        aws ecs describe-task-definition --task-definition $TASK_DEFINITION_ARN > orig-taskdef.json
        cat orig-taskdef.json | jq '.taskDefinition | .containerDefinitions[].image = "'$IMAGE_COMMIT_TAG'" | del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)' > taskdef.json
        cat taskdef.json

        task_definition_arn=$(aws ecs register-task-definition \
                                --family "${PREFIX}-${SERVICE}" \
                                --cli-input-json file://taskdef.json  \
                                --query 'taskDefinition.taskDefinitionArn' \
                                --output text)
        echo "Updating the service with the task definition arn: $task_definition_arn."
        echo ""
        echo "=============== UPDATING SERVICE ==============="
        aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "${PREFIX}-${SERVICE}" \
        --task-definition "$task_definition_arn" \
        --force-new-deployment
    fi
}

update_task_definition
