import json
from pydantic import BaseModel, Field

from openai_client import client

 
class EvaluationResult(BaseModel):
    score: int = Field(default=0, ge=0, le=100)
    reason: str
    missing_requirements: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    
    


def evaluate_task(task, request, evidence, output):

    system_prompt = (
        'You are the Evaluation component of an Engineering '
        'Research and Workflow Agent.\n\n'

        'Your responsibility is to independently evaluate whether '
        'the output produced for a task satisfies its completion criteria.\n\n'

        'EVALUATION RULES:\n'

        '1. Evaluate the output against the task description and '
        'completion criteria. Do not evaluate based on whether the '
        'output simply sounds convincing.\n\n'

        '2. Consider the original user request to ensure the task '
        'contributes to the overall objective.\n\n'

        '3. Examine the supplied evidence before accepting factual claims. '
        'Claims must be supported by the available evidence.\n\n'

        '4. Identify requirements that are missing, incomplete, or '
        'only partially satisfied.\n\n'

        '5. Identify unsupported claims, fabricated information, '
        'or conclusions that cannot be established from the evidence.\n\n'

        '6. Assign an objective score between 0 and 100 based on '
        'how completely and accurately the output satisfies the task.\n\n'

        'SCORING GUIDELINES:\n'

        '90-100: All requirements are satisfied with strong supporting evidence.\n'
        '80-89: Requirements are substantially satisfied, with only minor issues.\n'
        '60-79: Some requirements are satisfied, but important gaps remain.\n'
        '30-59: Significant requirements are missing or poorly addressed.\n'
        '0-29: The output fails to accomplish the task.\n\n'

        'IMPORTANT RESTRICTIONS:\n'

        '- Never invent evidence or assume a tool executed successfully.\n'
        '- Never treat the model output itself as proof that an action occurred.\n'
        '- Do not overlook unsupported claims because the overall answer is good.\n'
        '- Be objective and consistent in your scoring.\n\n'

        'Return your evaluation using the provided structured output schema.'
    )

    task_details = {
        'task_id': task.task_id,
        'description': task.description,
        'completion_criteria': task.completion_criteria,
        'task_type': task.task_type
    }

    user_prompt = (
        f'ORIGINAL USER REQUEST:\n{request}\n\n'

        f'TASK DETAILS:\n'
        f'{json.dumps(task_details, indent=2)}\n\n'

        f'EVIDENCE:\n'
        f'{json.dumps(evidence, indent=2, default=str)}\n\n'

        f'TASK OUTPUT:\n{output}\n\n'

        'Evaluate this task using the system instructions.'
    )

    response = client.responses.parse(
        model='gpt-5.4-mini',
        input=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_prompt
            }
        ],
        text_format=EvaluationResult
    )

    evaluation = response.output_parsed

    if evaluation is None:
        raise ValueError('The evaluator returned no structured result.')

    return evaluation


def is_evaluation_acceptable(evaluation):
    if (
        evaluation.score >= 80
        and not evaluation.missing_requirements
        and not evaluation.unsupported_claims
    ):
        return True

    return False



if __name__ == "__main__":
    # Test 1: High score, no issues
    test_1 = EvaluationResult(
        score=90,
        reason="All task requirements were satisfied.",
        missing_requirements=[],
        unsupported_claims=[],
    )

    # Test 2: Score below the passing threshold
    test_2 = EvaluationResult(
        score=68,
        reason="Some task requirements were not satisfied.",
        missing_requirements=[],
        unsupported_claims=[],
    )

    # Test 3: High score but contains unsupported claims
    test_3 = EvaluationResult(
        score=95,
        reason="The output is strong but contains an unsupported claim.",
        missing_requirements=[],
        unsupported_claims=[
            "One conclusion is not supported by the supplied evidence."
        ],
    )

    print("\n========== ACCEPTANCE TESTS ==========\n")

    print("Test 1:", is_evaluation_acceptable(test_1))
    print("Test 2:", is_evaluation_acceptable(test_2))
    print("Test 3:", is_evaluation_acceptable(test_3))
