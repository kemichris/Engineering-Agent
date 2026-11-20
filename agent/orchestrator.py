from openai_client import client
from agent.tool_registry import tools
from agent.tool_executor import execute_tool

# Managest  the agent loop
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
                output = execute_tool(item)
                tool_outputs.append(
                    output
                )

        if not tool_outputs:
            return response.output_text

        response = client.responses.create(
            model="gpt-5.4-mini", 
            previous_response_id=response.id, 
            input=tool_outputs
        )
