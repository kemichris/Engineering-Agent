from tools.github import get_repository_info

result = get_repository_info('openai/openai-python')

print(result)

result = get_repository_info('unknown/repository')
print(result)