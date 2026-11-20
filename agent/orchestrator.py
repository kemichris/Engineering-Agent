import json

from openai_client import client
from agent.tool_registry import tools, tool_functions


def run_agent(user_input):
    response = client.responses.create(
        model="gpt-5.4-mini", 
        tools=tools, 
        tool_choice="auto", 
        input=user_input
    )

    while True:
        tool_outputs = []

        for item in response.output:

            if item.type == "function_call":
                function = tool_functions.get(item.name)

                if function is None:
                    output = {"error": f"Tool {item.name} is not registered."}

                else:
                    try:
                        arguments = json.loads(item.arguments)

                        result = function(**arguments)

                        output = result

                    except Exception as error:
                        output = {"error": str(error)}

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(output),
                    }
                )

        if not tool_outputs:
            return response.output_text

        response = client.responses.create(
            model="gpt-5.4-mini", 
            previous_response_id=response.id, 
            input=tool_outputs
        )
