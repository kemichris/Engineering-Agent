import json
from openai_client import client
from agent.tool_registry import tools
from tools.github import get_repository_info

response = client.responses.create(
    model='gpt-5.4-mini',
    tools=tools,
    tool_choice='required',
    input='Get information about the openai/openai-python repository.'
)

# print(response)

for item in response.output:
    print('Type:', item.type)

    if item.type == 'function_call':
        data = json.loads(item.arguments)
        print('Tool:', item.name)
        print('Arguments:', item.arguments)
        print('Call ID:', item.call_id)
        result = get_repository_info(data['repo_name'])

        print('Result:', result)

        tool_output = {
            'type': 'function_call_output',
            'call_id': item.call_id,
            'output': json.dumps(result)
        }

        response = client.responses.create(
            model='gpt-5.4-mini',
            previous_response_id=response.id,
            input= [tool_output]
        )

        print('Final output', response.output_text)



