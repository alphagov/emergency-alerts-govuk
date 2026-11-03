from unittest.mock import ANY, patch

import pytest

from app.models.publish_task_progress import PublishTaskProgress


@pytest.mark.parametrize(
    "progress_id, progress_status, expect_run",
    [
        (
            # Assuming a manual run via SQS/an old API so we don't have an ID
            None,
            None,
            True,
        ),
        ("test", "pending", True),
        ("test", "in_progress", True),  # To account for retried tasks
        ("test", "cancelled", False),
    ],
)
@patch("app.notify_client.alerts_api_client.publish_api_client.upsert_publish_task")
@patch("app.notify_client.alerts_api_client.publish_api_client.get_publish_task")
def test_create_or_transition_returns_false_for_cancelled(
    mock_get_publish_task,
    mock_upsert_publish_task,
    progress_id,
    progress_status,
    expect_run,
):
    mock_get_publish_task.return_value = {
        "id": progress_id,
        "task_id": "test",
        "started_at": "test",
        "status": progress_status,
        "last_activity_at": "test",
    }

    progress_obj = PublishTaskProgress.create_or_transition(
        publish_origin="any",
        publish_type="any",
        pending_id=progress_id,
        trace_id="trace",
    )

    assert bool(progress_obj) == expect_run

    if expect_run:
        mock_upsert_publish_task.assert_called_once_with(
            pending_id=progress_id,
            trace_id="trace",
            task_id=ANY,
        )
    else:
        mock_upsert_publish_task.assert_not_called()
