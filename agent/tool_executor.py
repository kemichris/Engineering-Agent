import json

from agent.tool_registry import tool_functions, tool_schemas


# Handles tool execution and tracks its outcome.
def execute_tool(item):

    function = tool_functions.get(item.name)
    schema = tool_schemas.get(item.name)

    success = False
    result = None
    error_message = None

    if function is None:
        error_message = f'Tool {item.name} is not registered.'

    elif schema is None:
        error_message = (
            f'Tool {item.name} has no registered validation schema.'
        )

    else:
        try:
            # Parse the arguments returned by the model.
            arguments = json.loads(item.arguments)

            # Validate arguments against the registered Pydantic schema.
            validated_args = schema.model_validate(arguments).model_dump()

            # Execute the actual Python function.
            result = function(**validated_args)

            # Check whether the function returned an error.
            if isinstance(result, dict) and 'error' in result:
                error_message = result['error']

            else:
                success = True

        except Exception as error:
            error_message = str(error)

    # Prepare the output that will be sent back to OpenAI.
    if success:
        output = result
    else:
        output = {
            'error': error_message
        }

    tool_output = {
        'type': 'function_call_output',
        'call_id': item.call_id,
        'output': json.dumps(output)
    }

    # Return both OpenAI's required output and local execution metadata.
    return {
        'success': success,
        'tool_name': item.name,
        'tool_output': tool_output,
        'result': result,
        'error': error_message
    }
