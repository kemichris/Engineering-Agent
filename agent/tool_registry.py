tools = [
    {
        'type': 'function',
        'name': 'get_repository_info',
        'description': 'Get basic information about a GitHub repository.',
        'parameters': {
            'type': 'object',
            'properties': {
                'repo_name': {
                    'type': 'string',
                    'description': 'Repository name in owner/name format.'
                }
            },
            'required': ['repo_name'],
            'additionalProperties': False
        },
        'strict': True
    }
]