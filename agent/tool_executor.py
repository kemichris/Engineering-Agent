import json

from agent.tool_registry import tool_functions, tool_schemas

# Handles tool execution
def execute_tool(item):
    function = tool_functions.get(item.name)
    schema = tool_schemas.get(item.name)

    if function is None:
        output = {
            'error': f'Tool {item.name} is not registered.'
        }

    elif schema is None:
        output = {
            'error': f'Tool {item.name} has no registered validation schema.'
        }
    else:
        try:
            arguments = json.loads(item.arguments)
            validated_args = schema.model_validate(arguments).model_dump()
            result = function(**validated_args)

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
