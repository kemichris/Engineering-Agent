import requests


# Executes GitHub operations
def get_repository_info(repo_name):
    url = f"https://api.github.com/repos/{repo_name}"

    try:
        response = requests.get(url, timeout=15)

        # Raise an exception for unsuccessful HTTP responses
        response.raise_for_status()

        # Convert GitHub's JSON response into a Python dictionary
        data = response.json()

        return {
            "name": data.get("name"),
            "owner": data.get("owner", {}).get("login"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
        }

    except requests.exceptions.HTTPError as error:
        if response.status_code == 404:
            return {"error": "Repository not found."}

        return {"error": f"GitHub API returned an HTTP error: {error}"}

    except requests.exceptions.Timeout:
        return {"error": "GitHub API request timed out."}

    except requests.exceptions.RequestException as error:
        return {"error": f"GitHub API request failed: {error}"}

    except ValueError:
        return {"error": "GitHub returned an invalid JSON response."}


def get_repository_issues(repo_name, state='open', per_page=10, page=1):
    url = f'https://api.github.com/repos/{repo_name}/issues'

    try:
        issues = []
        current_page = page

        while len(issues) < per_page:
            response = requests.get(
                url,
                params={
                    'state': state,
                    'per_page': per_page,
                    'page': current_page
                },
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            # Stop if GitHub has no more results
            if not data:
                break

            # Process each record on the current page
            for issue in data:

                # Skip pull requests
                if issue.get('pull_request'):
                    continue

                issue_data = {
                    'issue_number': issue.get('number'),
                    'title': issue.get('title'),
                    'state': issue.get('state'),
                    'author': issue.get('user', {}).get('login'),
                    'url': issue.get('html_url'),
                    'creation_date': issue.get('created_at'),
                    'comment_count': issue.get('comments')
                }

                issues.append(issue_data)

                # Stop when we have enough actual issues
                if len(issues) >= per_page:
                    break

            # Move to the next GitHub page
            current_page += 1

        return issues

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



def get_issue_details(repo_name, issue_number):
    url = f'https://api.github.com/repos/{repo_name}/issues/{issue_number}'

    try:
        response = requests.get(url, timeout=15)

        response.raise_for_status()

        data = response.json()

        return {
            'issue_number': data.get('number'),
            'title': data.get('title'),
            'body': data.get('body'),
            'state': data.get('state'),
            'author': data.get('user', {}).get('login'),
            'labels': [
                label.get('name')
                for label in data.get('labels', [])
            ],
            'assignees': [
                assignee.get('login')
                for assignee in data.get('assignees', [])
            ],
            'url': data.get('html_url'),
            'creation_date': data.get('created_at'),
            'updated_date': data.get('updated_at'),
            'comment_count': data.get('comments')
        }

    except requests.exceptions.HTTPError as error:
        if response.status_code == 404:
            return {'error': 'Repository or issue not found.'}

        return {'error': f'GitHub API returned an HTTP error: {error}'}

    except requests.exceptions.Timeout:
        return {'error': 'GitHub API request timed out.'}

    except requests.exceptions.RequestException as error:
        return {'error': f'GitHub API request failed: {error}'}

    except ValueError:
        return {'error': 'GitHub returned an invalid JSON response.'}


if __name__ == '__main__':
    result = get_issue_details('facebook/react', 38183)

    print(result)
