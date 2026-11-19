import json

from openai_client import client
from agent.tool_registry import tools
from tools.github import get_repository_info


def run_agent(user_input):
    response = client.responses.create(
        model='gpt-5.4-mini',
        tools=tools,
        tool_choice='auto',
        input=user_input
    )

    while True:
        tool_outputs = []

        for item in response.output:

            if item.type == 'function_call':

                if item.name == 'get_repository_info':
                    arguments = json.loads(item.arguments)

                    result = get_repository_info(
                        arguments['repo_name']
                    )

                    tool_outputs.append({
                        'type': 'function_call_output',
                        'call_id': item.call_id,
                        'output': json.dumps(result)
                    })

        if not tool_outputs:
            return response.output_text

        response = client.responses.create(
            model='gpt-5.4-mini',
            previous_response_id=response.id,
            input=tool_outputs
        )
