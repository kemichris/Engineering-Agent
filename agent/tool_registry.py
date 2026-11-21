from pydantic import BaseModel, Field
from typing import Literal
from tools.github import get_repository_info

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

class GetRepositoryInfoArgs(BaseModel):
    repo_name: str

class GetRepositoryIssuesArgs(BaseModel):
    repo_name: str
    state: Literal['open', 'closed', 'all'] = 'open'
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)

# Resolves available functions
tool_functions = {
    'get_repository_info': get_repository_info
}

tool_schemas = {
    'get_repository_info': GetRepositoryInfoArgs
}

