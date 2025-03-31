# Orchestrators in Moya

Orchestrators in Moya are responsible for coordinating the actions of multiple agents. They enable complex workflows by managing interactions between agents and ensuring tasks are executed in the correct sequence.

## Overview

Orchestrators serve the following purposes:

- **Task Coordination**: Manage the flow of tasks between agents.
- **Collaboration**: Facilitate collaboration between multiple agents to solve complex problems.
- **Workflow Management**: Define and execute workflows involving multiple steps and agents.

## Key Components

### 1. BaseOrchestrator

**File:** `moya/orchestrators/base_orchestrator.py`

The `BaseOrchestrator` class provides the foundation for all orchestrator implementations in Moya. It defines the basic structure and methods that all orchestrators must implement.

#### Key Methods:
- `add_agent(agent: Agent) -> None`: Adds an agent to the orchestrator.
- `execute_workflow(workflow: dict) -> Any`: Executes a workflow defined as a dictionary.

#### Example Usage:
```python
from moya.orchestrators.base_orchestrator import BaseOrchestrator

class CustomOrchestrator(BaseOrchestrator):
    def __init__(self):
        self.agents = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def execute_workflow(self, workflow):
        # Custom workflow execution logic
        return "Workflow executed"

orchestrator = CustomOrchestrator()
orchestrator.add_agent("Agent1")
print(orchestrator.execute_workflow({"task": "example"}))
```

### 2. SequentialOrchestrator

**File:** `moya/orchestrators/sequential_orchestrator.py`

The `SequentialOrchestrator` class executes tasks in a sequential manner. It ensures that each task is completed before moving on to the next.

#### Key Features:
- Executes tasks in a predefined order.
- Supports error handling for individual tasks.

#### Example Usage:
```python
from moya.orchestrators.sequential_orchestrator import SequentialOrchestrator

orchestrator = SequentialOrchestrator()
orchestrator.add_agent("Agent1")
orchestrator.add_agent("Agent2")
result = orchestrator.execute_workflow({"tasks": ["task1", "task2"]})
print(result)
```

### 3. ParallelOrchestrator

**File:** `moya/orchestrators/parallel_orchestrator.py`

The `ParallelOrchestrator` class executes tasks in parallel. It is useful for workflows where tasks can be performed independently.

#### Key Features:
- Executes tasks concurrently.
- Aggregates results from all tasks.

#### Example Usage:
```python
from moya.orchestrators.parallel_orchestrator import ParallelOrchestrator

orchestrator = ParallelOrchestrator()
orchestrator.add_agent("Agent1")
orchestrator.add_agent("Agent2")
result = orchestrator.execute_workflow({"tasks": ["task1", "task2"]})
print(result)
```

## Custom Orchestrators

You can create custom orchestrators by extending the `BaseOrchestrator` class. This allows you to implement workflows tailored to your specific use case.

#### Example:
```python
from moya.orchestrators.base_orchestrator import BaseOrchestrator

class CustomOrchestrator(BaseOrchestrator):
    def __init__(self):
        self.agents = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def execute_workflow(self, workflow):
        # Custom workflow execution logic
        return "Custom workflow executed"

orchestrator = CustomOrchestrator()
orchestrator.add_agent("Agent1")
print(orchestrator.execute_workflow({"task": "example"}))
```

## Additional Notes

- Use `SequentialOrchestrator` for workflows that require strict task order.
- Use `ParallelOrchestrator` for workflows with independent tasks.
- Ensure that orchestrators are thread-safe if used in multi-threaded environments.
- Refer to the individual orchestrator class files for more details on configuration and usage.