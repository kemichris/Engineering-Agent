from agent.orchestrator import run_agent


def main():
    user_input = input('What would you like me to investigate? ')

    result = run_agent(user_input)

    print('\nAgent response:')
    print(result)


if __name__ == '__main__':
    main()
