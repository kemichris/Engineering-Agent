# Engineering Research & Workflow Agent

An AI-powered engineering research agent that investigates GitHub
repositories and issues using real GitHub data. The project is being
built incrementally in Python with the OpenAI Responses API, function
calling, Pydantic validation, and the GitHub REST API.

> **Project status:** Working prototype / pre-MVP. The core read-only
> GitHub research workflow is implemented and tested locally. It is not
> yet production-ready or deployed.

## 1. Project vision

The goal is to build an agent that can investigate engineering work
rather than simply answer questions. Given a request, it should
understand the objective, gather relevant repository data, inspect
selected issues and discussions, reason over the evidence, prepare
recommendations, and eventually carry out approved workflow actions.

The initial focus is GitHub repository and issue investigation. The
longer-term system will support planning, multi-step execution,
persistent task state, human approval, and reliable reporting.

## 2. Current capabilities

The following capabilities have been implemented and tested locally:

-   OpenAI Responses API connection using the Python SDK.
-   Dynamic tool selection and dispatch through a registry.
-   Local execution of model-requested function calls.
-   Pydantic validation of tool arguments.
-   Real GitHub REST API integration.
-   Repository metadata retrieval.
-   Issue listing with state filtering and pagination.
-   Filtering pull requests out of issue results (GitHub's Issues
    endpoints can return both issues and pull requests).
-   Retrieval of full details for a specific issue.
-   Retrieval of issue comments.
-   Multi-step tool use: retrieve a list of issues, select one, fetch
    its details, and combine the results.
-   Error responses for common HTTP, timeout, request, and JSON parsing
    failures.

### Current GitHub tools

  -----------------------------------------------------------------------
  Tool                                Responsibility
  ----------------------------------- -----------------------------------
  `get_repository_info`               Retrieves repository owner,
                                      description, language, stars,
                                      forks, and open issue count.

  `get_repository_issues`             Retrieves issue summaries with
                                      state filtering and pagination.
                                      Pull requests are excluded from the
                                      returned issue list.

  `get_issue_details`                 Retrieves the full description and
                                      metadata for one issue.

  `get_issue_comments`                Retrieves comments for one issue,
                                      including author, body, dates, and
                                      URL.
  -----------------------------------------------------------------------

## 3. Example workflow already demonstrated

User request:

> Find 5 open issues from `facebook/react` and give me the details of
> the first issue.

The agent successfully: 1. Interpreted the request. 2. Called
`get_repository_issues`. 3. Received a list of issue summaries. 4.
Selected the first issue from the results. 5. Called `get_issue_details`
with the selected issue number. 6. Combined the results into one
response.

A second test asked the agent to investigate issue `38183` in
`facebook/react`, retrieve its full details, read its comments, and
explain the reported problem and suggested solutions. The agent
successfully coordinated the issue-details and comments tools and
produced a consolidated investigation report.

These are local prototype tests, not a claim of production reliability.

## 4. Current architecture

``` text
User
 |
 v
main.py
 |
 v
agent/orchestrator.py
 |                  \
 |                   \---- OpenAI Responses API
 |                               |
 |                         Tool call request
 |                               |
 v                               v
agent/tool_executor.py <--- agent/tool_registry.py
 |                               |
 |                         Tool definitions
 |                         Function mapping
 |                         Pydantic schemas
 v
tools/github.py
 |
 v
GitHub REST API
 |
 v
Tool result returned to OpenAI
 |
 v
Final response to user
```

### Component responsibilities

-   **`main.py`** --- local command-line entry point; collects user
    input and prints the agent response.
-   **`openai_client.py`** --- loads environment variables and
    initializes the OpenAI client.
-   **`agent/orchestrator.py`** --- sends user input to the model,
    detects function calls, coordinates tool execution, sends tool
    outputs back, and continues until the model returns a final
    response.
-   **`agent/tool_registry.py`** --- defines the tools exposed to the
    model, maps tool names to Python functions, and maps tool names to
    Pydantic argument schemas.
-   **`agent/tool_executor.py`** --- parses tool arguments, validates
    them, executes the matching function, and packages the result as a
    function-call output.
-   **`tools/github.py`** --- contains GitHub API integration functions
    and their HTTP/JSON error handling.

### Current project structure

``` text
engineering-agent/
├── .env
├── .gitignore
├── main.py
├── openai_client.py
├── agent/
│   ├── __init__.py
│   ├── tool_registry.py
│   ├── tool_executor.py
│   └── orchestrator.py
└── tools/
    ├── __init__.py
    └── github.py
```

This is the structure established in the current implementation. New
modules should be introduced when a capability needs them, rather than
creating empty architecture files prematurely.

## 5. How tool calling works

1.  The user submits a request.
2.  The orchestrator sends the request and available tool definitions to
    the model.
3.  The model may return a function-call request.
4.  The executor looks up the requested function and its Pydantic
    schema.
5.  The executor parses and validates the arguments.
6.  The local Python function calls the GitHub API.
7.  The executor sends the tool result back to the model using the
    matching `call_id`.
8.  The model may request another tool or produce a final answer.

The model chooses and requests tools; the application executes the
Python functions. The model does not directly execute local Python code.

## 6. Milestones

### Completed

  Milestone                                Result
  ---------------------------------------- ------------------------
  Python project and virtual environment   Created
  OpenAI API connection                    Working
  First function-calling agent             Working
  Dynamic tool registry and dispatch       Implemented
  Tool executor separation                 Implemented
  Pydantic argument validation             Implemented
  Real GitHub repository lookup            Implemented
  GitHub issue listing and filtering       Implemented
  Issue pagination                         Implemented and tested
  Full issue detail retrieval              Implemented and tested
  Issue comment retrieval                  Implemented and tested
  Multi-step tool workflow                 Demonstrated locally

### Planned

  -----------------------------------------------------------------------
  Priority                Milestone               Intended outcome
  ----------------------- ----------------------- -----------------------
  Next                    Planning and task       Convert a user goal
                          decomposition           into explicit, ordered
                                                  steps.

  Next                    Execution state and     Track pending, running,
                          step tracking           completed, and failed
                                                  steps.

  Next                    Better tool and API     Distinguish validation,
                          error handling          not-found, rate-limit,
                                                  timeout, and transient
                                                  failures.

  Next                    Comment pagination and  Handle issues with
                          retrieval limits        large discussions
                                                  safely.

  Next                    Tests                   Add unit and
                                                  integration tests for
                                                  tools, validation,
                                                  executor, and
                                                  orchestrator.

  Later                   Persistent storage      Save tasks, plans,
                                                  execution events, and
                                                  results in a database.

  Later                   Human approval and      Require explicit
                          policy layer            approval before
                                                  consequential actions.

  Later                   Reliability controls    Add bounded tool loops,
                                                  retries where
                                                  appropriate, timeouts,
                                                  and execution limits.

  Later                   Observability and       Record tool traces and
                          evaluation              measure task
                                                  completion,
                                                  correctness, and
                                                  failure modes.

  Later                   API and deployment      Add a service
                                                  interface,
                                                  containerization,
                                                  configuration, and
                                                  deployment.
  -----------------------------------------------------------------------

## 7. MVP definition and rollout

### Proposed MVP

The first MVP should remain **read-only** and focus on one dependable
use case:

> Investigate a GitHub repository's issues and produce an evidence-based
> engineering report.

A user should be able to ask the agent to: - Inspect repository
metadata. - Find a specified number of open or closed issues. - Filter
and paginate issue results. - Retrieve full details for selected
issues. - Read their comments. - Summarize the reported problem,
relevant discussion, possible workarounds, and unanswered questions. -
Link findings back to their GitHub sources.

### MVP exit criteria

Before calling it ready for an external rollout, the project should
have:

-   Reliable argument validation and clear error messages.
-   A bounded execution loop so the agent cannot call tools
    indefinitely.
-   API rate-limit awareness and safe handling of transient failures.
-   Pagination and result limits for both issues and comments.
-   Tests covering successful calls, invalid arguments, missing
    repositories/issues, timeouts, and empty results.
-   A record of which tools were called and what evidence informed the
    report.
-   Clear handling of untrusted repository and issue content; content
    retrieved from GitHub must be treated as data, not instructions.
-   Secrets kept out of source control and logs.
-   A documented local setup and repeatable run instructions.

### Not in the first MVP

-   Automatically creating, editing, closing, or commenting on GitHub
    issues.
-   Merging pull requests or changing repository settings.
-   Autonomous code changes.
-   Unreviewed actions on behalf of a user.

Write-capable actions should come later behind explicit human approval
and a policy layer.

## 8. Setup and local execution

### Requirements

-   Python (use a supported version compatible with the installed
    dependencies).
-   An OpenAI API key.
-   Internet access for GitHub API requests.

### Setup

``` bash
git clone <your-repository-url>
cd engineering-agent

python3 -m venv .venv
source .venv/bin/activate

pip install openai python-dotenv requests pydantic
```

Create a `.env` file in the project root:

``` env
OPENAI_API_KEY=your_openai_api_key
```

Do not commit `.env`. Ensure `.gitignore` contains:

``` gitignore
.env
.venv/
__pycache__/
*.py[cod]
```

Run the agent from the project root:

``` bash
python3 main.py
```

The current command-line entry point prompts for an investigation
request.

## 9. Example prompts

``` text
Get information about openai/openai-python.
```

``` text
Find 10 open issues from facebook/react.
```

``` text
Find 5 open issues from facebook/react and give me the details of the first issue.
```

``` text
Investigate issue 38183 in facebook/react. Retrieve its full details and read the comments. Explain the reported problem and any solutions suggested in the discussion.
```

## 10. Engineering principles

-   **Separation of concerns:** API clients, tool definitions,
    validation, execution, and orchestration have distinct
    responsibilities.
-   **Read-only first:** Build reliable research capabilities before
    adding write actions.
-   **Validate at boundaries:** Treat model-generated arguments as
    untrusted input and validate them before execution.
-   **Bound execution:** Tool loops and API requests need explicit
    limits.
-   **Evidence-based reporting:** Findings should be traceable to
    repository, issue, and comment sources.
-   **Human control:** Consequential actions require approval.
-   **Incremental architecture:** Add components when the project needs
    them, and test each milestone before expanding.

## 11. References

-   [GitHub REST API:
    Issues](https://docs.github.com/en/rest/issues/issues)
-   [GitHub REST API: Issue
    comments](https://docs.github.com/en/rest/issues/comments)
-   [GitHub REST API:
    Pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
-   [OpenAI API documentation](https://platform.openai.com/docs)

------------------------------------------------------------------------

**Status note:** This README describes the implementation and tests
completed so far, alongside the proposed roadmap. Planned capabilities
are not represented as already implemented.
