repositories = {
    'openai/openai-python': {
        'name': 'openai-python',
        'owner': 'openai',
        'language': 'Python',
        'description': 'Official OpenAI Python SDK'
    }
}

# Executes GitHub operations
def get_repository_info(repo_name):
    if repo_name in repositories:
        return repositories[repo_name]
    else:
        return {'error': 'Repository not found'}
    