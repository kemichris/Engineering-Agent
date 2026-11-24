
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
                    '14. Do not select tools or assign tool names.\n'
                    '15. Do not assume that information from previous tasks '
                    'has already been retrieved.\n\n'
                    '16. Define clear completion criteria for every task.\n'
                    '17. Completion criteria must describe observable outcomes '
                    'that can be checked before a task is marked completed.\n'
                    '18. Make completion criteria specific to the task type.\n'
                    '19. Retrieval tasks must specify the expected data or evidence.\n'
                    '20. Analysis tasks must specify the expected analysis output.\n'
                    '21. Synthesis tasks must specify the expected final deliverable.\n'

                    'Return a complete execution plan containing task IDs, '
                    'descriptions, completion criteria and dependencies.'
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
                description=task.description,
                completion_criteria=task.completion_criteria,
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
