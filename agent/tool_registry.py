from pydantic import BaseModel, Field
from typing import Literal

from tools.github import get_repository_info, get_repository_issues


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
    },
    {
        'type': 'function',
        'name': 'get_repository_issues',
        'description': 'Get issues from a GitHub repository. Supports filtering by state and pagination.',
        'parameters': {
            'type': 'object',
            'properties': {
                'repo_name': {
                    'type': 'string',
                    'description': 'Repository name in owner/name format.'
                },
                'state': {
                    'type': 'string',
                    'enum': ['open', 'closed', 'all'],
                    'description': 'Issue state to retrieve. Defaults to open.'
                },
                'per_page': {
                    'type': 'integer',
                    'description': 'Number of issues to retrieve, between 1 and 100. Defaults to 10.'
                },
                'page': {
                    'type': 'integer',
                    'description': 'Page number to retrieve. Defaults to 1.'
                }
            },
            'required': ['repo_name'],
            'additionalProperties': False
        },
        'strict': False
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
    'get_repository_info': get_repository_info,
    'get_repository_issues': get_repository_issues
}


# Resolves validation schemas
tool_schemas = {
    'get_repository_info': GetRepositoryInfoArgs,
    'get_repository_issues': GetRepositoryIssuesArgs
}
