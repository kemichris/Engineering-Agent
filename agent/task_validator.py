from typing import Any

from agent.task_manager import Task, ValidationRequirements


def validate_retrieval(
    task: Task,
    execution_results: list[dict[str, Any]],
) -> dict:

    checks = []
    errors = []

    # Ensure this validator is being used for a retrieval task.
    if task.task_type != "retrieval":
        return {
            "valid": False,
            "checks": checks,
            "errors": ["This validator only supports retrieval tasks."],
        }

    # Get validation requirements from the task.
    requirements = task.validation_requirements

    expected_tool = requirements.expected_tool
    expected_count = requirements.expected_count
    required_fields = requirements.required_fields

    # Ensure an expected tool has been specified.
    if not expected_tool:
        return {
            "valid": False,
            "checks": checks,
            "errors": ["No expected tool was specified for this retrieval task."],
        }

    # Find the execution result from the expected tool.
    tool_results = [
        execution
        for execution in execution_results
        if execution.get("tool_name") == expected_tool
    ]

    if not tool_results:
        return {
            "valid": False,
            "checks": checks,
            "errors": [f"The {expected_tool} tool was not executed."],
        }

    # Check whether the tool executed successfully.
    execution = tool_results[-1]

    if not execution.get("success"):
        return {
            "valid": False,
            "checks": checks,
            "errors": [execution.get("error") or f"{expected_tool} retrieval failed."],
        }

    checks.append(f"{expected_tool} executed successfully.")

    # Extract the actual data returned by the tool.
    records = execution.get("result")

    if not isinstance(records, list):
        errors.append("The retrieval result is not a list.")
        return {"valid": False, "checks": checks, "errors": errors}

    checks.append("Retrieval result is a list.")

    # Validate the number of retrieved records.
    if expected_count is not None:
        if len(records) != expected_count:
            errors.append(
                f"Expected {expected_count} records, " f"but retrieved {len(records)}."
            )
        else:
            checks.append(f"Exactly {expected_count} records were retrieved.")

    # Ensure required fields have been specified.
    if not required_fields:
        errors.append("No required fields were specified for this retrieval task.")

    record_ids = []

    # Inspect every retrieved record.
    for index, record in enumerate(records, start=1):

        if not isinstance(record, dict):
            errors.append(f"Record {index} is not a dictionary.")
            continue

        # Check that all required fields exist.
        missing_fields = [field for field in required_fields if field not in record]

        if missing_fields:
            errors.append(
                f"Record {index} is missing fields: " f'{", ".join(missing_fields)}.'
            )
            continue

        # GitHub-specific validation.
        if expected_tool == "get_repository_issues":

            if not record.get("issue_number"):
                errors.append(f"Issue record {index} has no issue number.")
            else:
                record_ids.append(record["issue_number"])

            if not record.get("title"):
                errors.append(f"Issue record {index} has no title.")

            if record.get("state") != "open":
                errors.append(f"Issue record {index} is not open.")

            if not isinstance(record.get("labels"), list):
                errors.append(f"Issue record {index} has invalid labels.")

    # Check that GitHub issue numbers are unique.
    if expected_tool == "get_repository_issues":
        if len(record_ids) != len(set(record_ids)):
            errors.append("Duplicate issue numbers were retrieved.")
        else:
            checks.append("Issue numbers are unique.")

    # Record successful validation of all records.
    if not errors:
        checks.append("All records passed validation.")

    return {"valid": len(errors) == 0, "checks": checks, "errors": errors}
