import requests


# Executes GitHub operations
def get_repository_info(repo_name):
    url = f'https://api.github.com/repos/{repo_name}'

    try:
        response = requests.get(url, timeout=15)

        # Raise an exception for unsuccessful HTTP responses
        response.raise_for_status()

        # Convert GitHub's JSON response into a Python dictionary
        data = response.json()

        return {
            'name': data.get('name'),
            'owner': data.get('owner', {}).get('login'),
            'description': data.get('description'),
            'language': data.get('language'),
            'stars': data.get('stargazers_count'),
            'forks': data.get('forks_count'),
            'open_issues': data.get('open_issues_count')
        }

    except requests.exceptions.HTTPError as error:
        if response.status_code == 404:
            return {'error': 'Repository not found.'}

        return {'error': f'GitHub API returned an HTTP error: {error}'}

    except requests.exceptions.Timeout:
        return {'error': 'GitHub API request timed out.'}

    except requests.exceptions.RequestException as error:
        return {'error': f'GitHub API request failed: {error}'}

    except ValueError:
        return {'error': 'GitHub returned an invalid JSON response.'}
