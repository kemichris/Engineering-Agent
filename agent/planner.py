
from openai_client import client
from agent.task_manager import Plan, PlanDraft, Task


def create_plan(user_request: str) -> Plan:

    response = client.responses.parse(
        model='gpt-5.4-mini',

        input=[
            {
                'role': 'system',
                'content': (
                    'You are the planning component of an Engineering '
                    'Research and Workflow Agent.\n\n'

                    'Your responsibility is to convert user requests '
                    'into clear, ordered, and executable tasks.\n\n'

                    'PLANNING RULES:\n'
                    '1. Understand the overall objective of the user.\n'
                    '2. Break the objective into small, meaningful tasks.\n'
                    '3. Arrange tasks in the correct execution order.\n'
                    '4. Assign sequential task IDs starting from 1.\n'
                    '5. Give every task a clear and specific description.\n'
                    '6. Identify dependencies between tasks.\n'
                    '7. Use depends_on to reference prerequisite task IDs.\n'
                    '8. Tasks without prerequisites should have an empty '
                    'depends_on list.\n'
                    '9. Only create a dependency when a task genuinely requires '
                    'the output or completion of another task.\n'
                    '10. Do not create dependencies merely because one task '
                    'appears earlier in the plan.\n'
                    '11. Allow independent tasks to have no dependencies so '
                    'they can potentially execute concurrently.\n'
                    '12. Do not create unnecessary or redundant tasks.\n'
                    '13. Do not execute tasks or retrieve external information.\n'
                    '14. Do not assume that information from previous tasks '
                    'has already been retrieved.\n\n'

                    'COMPLETION CRITERIA:\n'
                    '15. Define clear completion criteria for every task.\n'
                    '16. Completion criteria must describe observable outcomes '
                    'that can be checked before a task is marked completed.\n'
                    '17. Make completion criteria specific to the task type.\n'
                    '18. Retrieval tasks must specify the expected data or evidence.\n'
                    '19. Analysis tasks must specify the expected analysis output.\n'
                    '20. Synthesis tasks must specify the expected final deliverable.\n\n'

                    'TASK CLASSIFICATION:\n'
                    'Every task must be classified using exactly one of '
                    'these types: retrieval, analysis, or synthesis.\n'
                    '21. Use retrieval for tasks that collect information from '
                    'external sources or tools.\n'
                    '22. Use analysis for tasks that examine retrieved information '
                    'and identify patterns or findings.\n'
                    '23. Use synthesis for tasks that combine findings into '
                    'a final report or recommendation.\n\n'

                    'STRUCTURED VALIDATION REQUIREMENTS:\n'
                    '24. Every retrieval task must define relevant validation requirements.\n'
                    '25. Specify expected_tool when a particular tool is required.\n'
                    '26. Specify expected_count when a specific number of records '
                    'is requested.\n'
                    '27. Specify required_fields when each retrieved record must '
                    'contain particular fields.\n'
                    '28. Only specify requirements relevant to the task.\n'
                    '29. Analysis and synthesis tasks should leave retrieval-specific '
                    'requirements empty.\n'
                    '30. Never invent tool names or output fields.\n\n'

                    'AVAILABLE GITHUB TOOLS:\n'
                    '- get_repository_info\n'
                    '- get_repository_issues\n'
                    '- get_issue_details\n'
                    '- get_issue_comments\n\n'

                    'AVAILABLE TOOL OUTPUT SCHEMAS:\n'
                    'get_repository_issues returns a list of issue records '
                    'containing these exact fields:\n'
                    '- issue_number\n'
                    '- title\n'
                    '- state\n'
                    '- author\n'
                    '- url\n'
                    '- creation_date\n'
                    '- comment_count\n'
                    '- body\n'
                    '- labels\n\n'

                    'When defining expected_tool, use the exact registered tool name.\n'
                    'When defining required_fields, use the exact field names '
                    'from the corresponding tool output.\n'
                    'Do not confuse API field names with the Python output '
                    'field names listed above.\n\n'

                    'The Planner may identify an expected tool for validation, '
                    'but must not execute tools or perform tool dispatch.\n\n'

                    'Return a complete execution plan containing task IDs, '
                    'task types, descriptions, completion criteria, '
                    'dependencies, and structured validation requirements.'
                )
            },
            {
                'role': 'user',
                'content': user_request
            }
        ],

        text_format=PlanDraft
    )

    if response.output_parsed is None:
        raise ValueError('The planner did not return a valid execution plan.')

    # Convert the Planner's output into our runtime Plan.
    plan_draft = response.output_parsed

    plan = Plan(
        tasks=[
            Task(
                task_id=task.task_id,
                task_type=task.task_type,
                description=task.description,
                completion_criteria=task.completion_criteria,
                validation_requirements=task.validation_requirements,
                depends_on=task.depends_on
            )
            for task in plan_draft.tasks
        ]
    )

    return plan


if __name__ == '__main__':

    plan = create_plan(
        'Investigate the five most recent open issues in facebook/react, '
        'identify recurring problems, and summarize them.'
    )

    print(plan.model_dump_json(indent=4))
