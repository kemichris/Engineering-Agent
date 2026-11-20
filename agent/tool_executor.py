import json

from agent.tool_registry import tool_functions


def execute_tool(item):
    function = tool_functions.get(item.name)

    if function is None:
        output = {
            'error': f'Tool {item.name} is not registered.'
        }
    else:
        try:
            arguments = json.loads(item.arguments)
            result = function(**arguments)

            output = result

        except Exception as error:
            output = {
                'error': str(error)
            }

    return {
        'type': 'function_call_output',
        'call_id': item.call_id,
        'output': json.dumps(output)
    }
