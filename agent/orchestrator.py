
from openai_client import client
from agent.tool_registry import tools
from agent.tool_executor import execute_tool
from agent.planner import create_plan
from agent.task_manager import TaskManager
from agent.task_validator import validate_retrieval


# Coordinates the complete agent workflow.
def run_agent(user_input):

    # Step 1: Generate the execution plan.
    plan = create_plan(user_input)

    # Step 2: Initialize the Task Manager.
    task_manager = TaskManager(plan)

    final_result = None

    # Step 3: Execute tasks until the plan is complete.
    while not task_manager.is_complete():

        # Get the next task whose dependencies are completed.
        next_task = task_manager.get_next_task()

        # Stop if no task is currently eligible for execution.
        if next_task is None:
            break

        print(f'\nExecuting Task {next_task.task_id}')
        print(next_task.description)

        print(f'Completion criteria: {next_task.completion_criteria}')

        # Mark the task as currently executing.
        task_manager.mark_processing(next_task.task_id)

        # Retrieve the results of the task's dependencies.
        dependency_results = []

        for dependency_id in next_task.depends_on:
            dependency_task = task_manager.get_task(dependency_id)

            dependency_results.append(
                f'Task {dependency_id} response:\n'
                f'{dependency_task.result["response"]}\n\n'
                f'Task {dependency_id} execution evidence:\n'
                f'{dependency_task.result["execution_results"]}'
            )

        # Prepare the execution context.
        task_input = (
            f'Original user request:\n{user_input}\n\n'
            f'Current task:\n{next_task.description}\n\n'
            f'Expected completion criteria:\n'
            f'{next_task.completion_criteria}\n\n'
            f'Previous task results:\n'
            f'{"\n\n".join(dependency_results)}\n\n'
            'Complete only the current task. '
            'Use the available tools when necessary. '
            'Do not attempt to execute future tasks.'
        )

        try:
            # Execute the current task using the existing tool loop.
            execution = run_tool_loop(task_input)

            result = execution['response']
            execution_results = execution['execution_results']

            # Check whether any tool execution failed.
            failed_tools = [
                tool_result
                for tool_result in execution_results
                if not tool_result['success']
            ]

            if failed_tools:

                error_messages = [
                    f"{tool_result['tool_name']}: "
                    f"{tool_result['error']}"
                    for tool_result in failed_tools
                ]

                error_summary = '; '.join(error_messages)

                # Mark the task as failed.
                task_manager.mark_failed(
                    next_task.task_id,
                    error_summary
                )

                print(
                    f'Task {next_task.task_id} failed: '
                    f'{error_summary}'
                )

                continue

            # Validate retrieval tasks before marking them completed.
            validation = None

            if next_task.task_type == 'retrieval':

                print(f'Validating Task {next_task.task_id}...')

                validation = validate_retrieval(
                    task=next_task,
                    execution_results=execution_results
                )

                # Display validation results.
                print('\nValidation checks:')
                for check in validation['checks']:
                    print(f'  [PASS] {check}')

                if not validation['valid']:

                    print('\nValidation errors:')

                    for error_message in validation['errors']:
                        print(f'  [FAIL] {error_message}')

                    error_summary = '; '.join(
                        validation['errors']
                    )

                    # Invalid evidence means the task has not completed.
                    task_manager.mark_failed(
                        next_task.task_id,
                        f'Validation failed: {error_summary}'
                    )

                    print(
                        f'\nTask {next_task.task_id} failed validation.'
                    )

                    continue

                print('\nRetrieval validation passed.')

            # Preserve the complete task execution record.
            task_result = {
                'response': result,
                'execution_results': execution_results,
                'validation': validation
            }

            # Save the complete result and mark the task as completed.
            task_manager.mark_completed(
                next_task.task_id,
                task_result
            )

            final_result = result

            print(f'Task {next_task.task_id} completed.')

        except Exception as error:

            # Record unexpected execution failures.
            task_manager.mark_failed(
                next_task.task_id,
                str(error)
            )

            print(f'Task {next_task.task_id} failed: {error}')

    # Step 4: Report final execution progress.
    progress = task_manager.get_progress()

    print('\nExecution progress:')
    print(progress)

    if not task_manager.is_successful():

        return (
            'Workflow finished with incomplete tasks.\n\n'
            f'Execution progress: {progress}\n\n'
            f'Last available result: {final_result}'
        )

    return final_result


# Handles model interaction and individual tool executions.
def run_tool_loop(user_input):

    response = client.responses.create(
        model='gpt-5.4-mini',
        tools=tools,
        tool_choice='auto',
        input=user_input
    )

    # Stores execution information for the application.
    execution_results = []

    while True:

        tool_outputs = []

        for item in response.output:

            if item.type == 'function_call':

                execution = execute_tool(item)

                # Preserve the complete execution result.
                execution_results.append({
                    'tool_name': execution['tool_name'],
                    'success': execution['success'],
                    'result': execution['result'],
                    'error': execution['error']
                })

                # Send only the OpenAI-compatible output to the model.
                tool_outputs.append(
                    execution['tool_output']
                )

        # Return when the model has no more tool calls.
        if not tool_outputs:
            return {
                'response': response.output_text,
                'execution_results': execution_results
            }

        response = client.responses.create(
            model='gpt-5.4-mini',
            previous_response_id=response.id,
            input=tool_outputs
        )


if __name__ == '__main__':

    result = run_agent(
        'Investigate the five most recent open issues in facebook/react, '
        'identify recurring problems, and summarize them.'
    )

    print('\n========== FINAL REPORT ==========\n')
    print(result)
