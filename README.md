# Engineering Research & Workflow Agent

An AI-powered engineering research and workflow agent that investigates
GitHub repositories and issues using real GitHub data. The project is
being built incrementally in Python with the OpenAI Responses API,
function calling, Pydantic validation, and the GitHub REST API.

> **Project status:** Working local prototype / pre-MVP. The agent can
> plan and execute multi-step GitHub research workflows, track task
> dependencies and outcomes, and produce investigation reports. It is
> not yet production-ready or deployed.

## 1. Project vision

The goal is to build an agent that can investigate engineering work
rather than simply answer questions. Given a request, it should
understand the objective, break it into tasks, gather relevant
repository data, inspect selected issues and discussions, reason over
the evidence, prepare recommendations, and eventually carry out approved
workflow actions.

The initial focus is read-only GitHub repository and issue
investigation. The longer-term system will support persistent workflows,
stronger completion validation, human approval, and reliable
evidence-backed reporting.

## 2. Current capabilities

The following capabilities have been implemented and exercised locally.

### Model and tool infrastructure

-   OpenAI Responses API connection using the Python SDK.
-   Dynamic tool selection and dispatch through a central registry.
-   Local execution of model-requested function calls.
-   Pydantic validation of model-generated tool arguments.
-   Separation between tool definitions, schemas, function mappings, and
    execution.
-   A reusable model/tool-calling loop that can execute multiple tool
    calls.
-   Tool execution metadata captured separately from the
    OpenAI-compatible function-call output.

### GitHub integration

-   Real GitHub REST API integration.
-   Repository metadata retrieval.
-   Issue listing with state filtering and pagination.
-   Pull requests filtered out of issue results.
-   Full details retrieval for a specific issue.
-   Issue comment retrieval.
-   HTTP, timeout, request, and JSON error handling in GitHub functions.

### Planning and workflow orchestration

-   A Planner that converts a natural-language objective into a
    structured task plan.
-   Tool-independent task planning: the Planner describes work and
    dependencies without hardcoding tool names.
-   Structured task descriptions and completion criteria.
-   Task dependencies represented through `depends_on`.
-   Plan validation for unique task IDs, unknown dependencies,
    self-dependencies, and circular dependencies.
-   A Task Manager that selects eligible tasks and tracks task state,
    results, errors, and progress.
-   Task states for pending, processing, completed, failed, and blocked
    work.
-   A high-level Orchestrator that coordinates planning, task execution,
    dependency-result handoff, and final workflow reporting.
-   Failed prerequisites prevent dependent tasks from running; dependent
    tasks are reported as blocked.
-   Tool failures are captured as execution metadata and can cause the
    current task to fail instead of silently treating an error response
    as successful work.

## 3. GitHub tools

  -----------------------------------------------------------------------
  Tool                                Responsibility
  ----------------------------------- -----------------------------------
  `get_repository_info`               Retrieves repository owner,
                                      description, language, stars,
                                      forks, and open issue count.

  `get_repository_issues`             Retrieves issue summaries with
                                      state filtering and pagination,
                                      excluding pull requests.

  `get_issue_details`                 Retrieves the full description and
                                      metadata for one issue, including
                                      labels and timestamps.

  `get_issue_comments`                Retrieves comments for one issue,
                                      including author, body, dates, and
                                      URL.
  -----------------------------------------------------------------------

## 4. Current architecture

The implementation has two coordination levels:

-   **High-level workflow orchestration:** plans the work, tracks task
    dependencies and state, and decides which task can run next.
-   **Low-level tool-calling loop:** lets the model request registered
    tools, executes those functions locally, and returns their outputs
    to the model.

``` text
User request
    |
    v
Planner
    |
    v
Plan + Task Manager
    |
    v
High-level Orchestrator
    |
    +---- selects eligible task
    |
    v
Task execution / model
    |
    v
Reusable tool-calling loop
    |
    +---- OpenAI Responses API
    |
    v
Tool Executor <---- Tool Registry
    |
    v
GitHub tools
    |
    v
GitHub REST API
    |
    v
Tool results + execution metadata
    |
    v
Task state update
    |
    v
Next eligible task / final report
```

### Component responsibilities

-   **`main.py`** --- local command-line entry point.
-   **`openai_client.py`** --- loads environment variables and
    initializes the OpenAI client.
-   **`agent/planner.py`** --- converts the user's objective into a
    structured plan with task descriptions, dependencies, and completion
    criteria.
-   **`agent/task_manager.py`** --- defines task and plan models,
    validates dependency graphs, tracks lifecycle state, selects
    eligible tasks, and reports progress.
-   **`agent/orchestrator.py`** --- coordinates the complete workflow,
    passes dependency results into later tasks, runs the tool loop, and
    updates task outcomes.
-   **`agent/tool_registry.py`** --- defines available tools, OpenAI
    function schemas, Pydantic argument schemas, and Python function
    mappings.
-   **`agent/tool_executor.py`** --- parses and validates tool
    arguments, executes the selected function, and returns both the
    tool-call output and local execution metadata.
-   **`tools/github.py`** --- contains GitHub API integration functions
    and their HTTP/JSON handling.

### Current project structure

``` text
Engineering-Agent/
├── .env
├── .gitignore
├── main.py
├── openai_client.py
├── agent/
│   ├── __init__.py
│   ├── planner.py
│   ├── task_manager.py
│   ├── orchestrator.py
│   ├── tool_registry.py
│   └── tool_executor.py
└── tools/
    ├── __init__.py
    └── github.py
```

This reflects the current implementation discussed and tested. Update
the structure as modules are added or responsibilities change.

## 5. How the workflow works

1.  The user submits an engineering research objective.
2.  The Planner creates a structured plan with task descriptions,
    completion criteria, and dependencies.
3.  Pydantic validates the plan, including unique task IDs and a valid
    acyclic dependency graph.
4.  The Task Manager identifies a pending task whose prerequisites have
    completed.
5.  The Orchestrator marks the task as processing and passes the outputs
    of its dependencies into the task context.
6.  The model can request registered GitHub tools through the reusable
    tool-calling loop.
7.  The Tool Executor validates arguments, invokes the Python function,
    and records whether the tool execution succeeded.
8.  The Orchestrator uses execution outcomes to update the task state.
9.  Failed tasks prevent dependent tasks from executing; those dependent
    tasks are marked blocked.
10. The workflow reports task progress and returns the final report when
    the plan succeeds, or an incomplete-workflow result when it does
    not.

The model requests tools; the application executes the Python functions.
The model does not directly execute local Python code.

## 6. Work completed and tested so far

### A. GitHub research tools

The agent has successfully:

-   Retrieved repository metadata.
-   Retrieved issue lists from `facebook/react`.
-   Paginated issue results and excluded pull requests.
-   Retrieved full details for a selected issue.
-   Retrieved comments for an issue.
-   Coordinated multiple tools in one investigation, allowing the model
    to select a relevant issue and then request its details and
    discussion.

One demonstrated investigation used issue `38183` in `facebook/react`
and retrieved its details and comments.

### B. Planner and Task Manager

The project now has a separate planning and task-state layer.

Implemented:

-   Structured `Plan`, `Task`, `PlanDraft`, and `TaskDraft` models.
-   Planner-generated task IDs, descriptions, dependencies, and
    completion criteria.
-   Dependency validation, including duplicate IDs, missing dependency
    IDs, self-dependencies, and cycles.
-   Eligible-task selection based on prerequisite completion.
-   Task lifecycle and progress tracking.
-   Failed and blocked task reporting.

The Planner was tested independently with:

``` bash
python3 -m agent.planner
```

### C. High-level Orchestrator

The Orchestrator has been tested with a multi-task GitHub investigation.
A successful run generated a plan, retrieved five recent open issues,
analyzed them, and produced a report that referenced issue numbers such
as `#38359`, `#38351`, `#38335`, `#38367`, and `#38345`.

The exact issue set is time-dependent; these issue numbers describe one
observed run, not a permanent expected result.

The workflow also demonstrated that a plan can be generated with three
dependent tasks and that task outputs can be passed to subsequent tasks.

### D. Failure propagation test

A GitHub API rate-limit response was encountered during an orchestrator
run. The workflow reported:

-   Task 1: failed.
-   Tasks 2--4: blocked.
-   Completed tasks: 0.
-   Failed tasks: 1.
-   Blocked tasks: 3.

This is an important reliability improvement: the application surfaced
the failed task and prevented dependent analysis from proceeding.

### E. Important current limitation

The Planner now produces `completion_criteria`, and the Orchestrator
displays them as part of each task. However, **deterministic task-level
completion validation is not yet implemented**.

A successful tool execution and a returned model response are not
sufficient proof that every task objective was fulfilled. The next
milestone is to validate task outputs against their completion criteria
and required evidence before marking tasks completed.

## 7. Current milestone status

  -----------------------------------------------------------------------
  Capability                          Status
  ----------------------------------- -----------------------------------
  OpenAI Responses API connection     Implemented and tested

  Dynamic tool registry and dispatch  Implemented and tested

  Pydantic tool argument validation   Implemented

  GitHub repository lookup            Implemented

  Issue listing, filtering, and       Implemented and tested
  pagination                          

  Full issue details                  Implemented and tested

  Issue comments                      Implemented and tested

  Multi-step tool-calling workflow    Demonstrated locally

  Planner and structured task         Implemented and tested
  generation                          

  Task dependency validation          Implemented and tested

  Task lifecycle and progress         Implemented and tested
  tracking                            

  High-level task orchestration       Demonstrated locally

  Tool failure propagation            Implemented and tested with a
                                      rate-limit failure

  Dependent-task blocking             Implemented and tested

  Completion criteria generation      Implemented

  Deterministic task completion       Not yet implemented
  validation                          

  GitHub rate-limit reset/wait/retry  Not yet implemented
  policy                              

  Persistent run history              Planned

  Evidence store and claim-level      Not yet complete
  traceability                        

  Human approval and write actions    Post-MVP
  -----------------------------------------------------------------------

## 8. Next engineering milestones

The next work should improve reliability before adding more integrations
or write capabilities.

### Priority 1 --- Task-level completion validation

A task must not be marked completed merely because the model returned
text or a tool call did not raise an exception.

Planned validation:

-   **Retrieval tasks:** verify the requested number of records,
    required fields, ordering, and source identifiers.
-   **Analysis tasks:** verify that the analysis accounts for the
    retrieved records and supports claims with issue references.
-   **Synthesis tasks:** verify that the report is based on the
    completed analysis and distinguishes recurring themes from outliers.
-   Store validation outcomes and reasons alongside task results.

Use deterministic Python checks for measurable requirements and
model-assisted evaluation only for semantic requirements.

### Priority 2 --- GitHub rate-limit handling

The agent has demonstrated that it can surface and propagate a
rate-limit failure. It still needs a deliberate recovery policy:

-   Inspect HTTP 403 rate-limit responses.
-   Read GitHub's `X-RateLimit-Reset` and related rate-limit headers.
-   Distinguish primary rate limits from other forbidden responses.
-   Decide whether to wait, retry within a bounded policy, or stop.
-   Report the retry time or reason the workflow cannot continue.

### Priority 3 --- Stronger evidence traceability

-   Preserve issue numbers, titles, URLs, and retrieval timestamps.
-   Keep retrieved source material associated with the task that used
    it.
-   Require report findings to reference supporting issues.
-   Clearly identify missing data and retrieval limitations.

### Priority 4 --- Reliability and tests

-   Add bounded task counts and model/tool-call iterations.
-   Add unit tests for plan validation and Task Manager transitions.
-   Test unknown tools, invalid arguments, API errors, timeouts, empty
    results, pagination, and pull-request filtering.
-   Test successful workflows and partial failures.
-   Test that a failed prerequisite blocks dependent tasks.
-   Add report-grounding checks.

### Later milestones

-   Persistent storage and resumable run history.
-   Cancellation and explicit retry policies.
-   More GitHub research capabilities and additional source
    integrations.
-   Human approval gates and write-capable tools.
-   Hosted API, background workers, authentication, and deployment.

## 9. MVP definition

The first MVP remains a **read-only GitHub engineering research agent**.

A user should be able to ask it to:

-   Inspect a public GitHub repository.
-   Retrieve a specified number of open, closed, or all issues within
    supported limits.
-   Retrieve issue details, labels, authors, timestamps, and comments.
-   Investigate multiple issues as one coordinated workflow.
-   Identify recurring themes and compare reported symptoms.
-   Produce a concise report with issue numbers, direct source links,
    and limitations.
-   Show task progress and report failed or blocked work accurately.

### MVP exclusions

-   Creating, editing, closing, or commenting on GitHub issues.
-   Creating branches, commits, or pull requests.
-   Autonomous code changes, test execution, or deployment.
-   Unreviewed consequential actions.
-   Unbounded agent loops or uncontrolled parallel execution.

Write-capable actions should remain outside the MVP until permissions,
explicit human approval, audit trails, and recovery controls are
designed.

## 10. Setup and local execution

### Requirements

-   Python compatible with the installed dependencies.
-   An OpenAI API key.
-   Internet access for GitHub API requests.

### Setup

``` bash
git clone <your-repository-url>
cd Engineering-Agent

python3 -m venv .venv
source .venv/bin/activate

pip install openai python-dotenv requests pydantic
```

Create a `.env` file in the project root:

``` env
OPENAI_API_KEY=your_openai_api_key
```

Do not commit `.env`. Ensure `.gitignore` includes:

``` gitignore
.env
.venv/
__pycache__/
*.py[cod]
```

Run the agent from the project root:

``` bash
python3 -m agent.orchestrator
```

Other useful module checks:

``` bash
python3 -m agent.planner
python3 -m agent.task_manager
python3 -m tools.github
```

The exact command available for an individual module depends on its
current `__main__` test block.

## 11. Example investigation requests

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

``` text
Investigate the five most recent open issues in facebook/react, identify recurring problems, and summarize them.
```

## 12. Engineering principles

-   **Separation of concerns:** planning, task state, orchestration,
    tool definitions, validation, and API integration have distinct
    responsibilities.
-   **Tool-independent planning:** the Planner describes work and
    dependencies without duplicating the tool registry.
-   **Two levels of coordination:** the high-level Orchestrator manages
    tasks; the reusable tool loop manages model/tool interactions.
-   **Read-only first:** build dependable research capabilities before
    adding write actions.
-   **Validate at boundaries:** model-generated tool arguments and task
    outputs must be checked before they are trusted.
-   **Failure visibility:** errors, blocked tasks, and partial
    completion must be explicit.
-   **Evidence before conclusions:** report claims should be traceable
    to GitHub sources.
-   **Bound execution:** task counts, tool iterations, API requests, and
    retries need explicit limits.
-   **Incremental architecture:** introduce components when needed and
    test each milestone before expanding.

## 13. Product architecture alignment

The Product Architecture & MVP Blueprint defines the north star as
turning an engineering objective into a structured, evidence-backed
workflow: understand the request, plan the work, gather information
through approved capabilities, analyze evidence, and deliver an
auditable outcome.

The current implementation has established the foundation for these
blueprint capabilities:

-   Request intake through a local command-line interface.
-   Planning and task dependency generation.
-   Task management and sequential orchestration.
-   Registered GitHub tool capabilities with schema validation.
-   GitHub issue and comment retrieval.
-   Initial failure visibility and blocked-task handling.
-   Initial analysis and report generation.

The following blueprint requirements remain important work rather than
completed features:

-   Deterministic completion validation.
-   A complete evidence store and claim-level source traceability.
-   Bounded runtime budgets and robust rate-limit recovery.
-   Persistent run/task history and resumability.
-   Comprehensive automated tests and security evaluation.
-   Hosted API, worker, and user-facing application layers.

The product blueprint is a target architecture, not a statement that all
listed capabilities have already been implemented.

## 14. References

-   [GitHub REST API:
    Issues](https://docs.github.com/en/rest/issues/issues)
-   [GitHub REST API: Issue
    comments](https://docs.github.com/en/rest/issues/comments)
-   [GitHub REST API:
    Pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
-   [GitHub REST API: Rate
    limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
-   [OpenAI API documentation](https://platform.openai.com/docs)

------------------------------------------------------------------------

**Status note:** This README distinguishes capabilities implemented and
tested in the current local prototype from planned product architecture.
Successful sample runs do not establish production reliability;
task-level completion validation, robust rate-limit recovery,
comprehensive tests, and full evidence traceability remain outstanding.
