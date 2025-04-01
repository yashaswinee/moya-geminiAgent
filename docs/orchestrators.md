# Moya Orchestrators

Orchestrators in Moya coordinate the flow of messages between users and agents. They are responsible for:

1. Receiving and routing user messages to the appropriate agent(s)
2. Managing conversation context and history
3. Combining responses from multiple agents when needed
4. Implementing custom workflows and agent collaboration patterns

This guide introduces the available orchestrators and explains how to use them effectively.

## Orchestrator Types

### 1. Orchestrator

The `Orchestrator` class provides the foundation for all orchestrator implementations in Moya. It defines the basic structure and methods that all orchestrators must implement.

```python
from moya.orchestrators.orchestrator import Orchestrator

class CustomOrchestrator(Orchestrator):
    def orchestrate(self, thread_id: str, user_message: str, **kwargs) -> str:
        # Your custom orchestration logic here
        pass
```

### 2. SimpleOrchestrator

**File:** `moya/orchestrators/simple_orchestrator.py`

The `SimpleOrchestrator` class is a straightforward implementation of the `Orchestrator` class. It is designed for simple use cases where a single agent is responsible for handling user messages.

#### Example Usage:
```python
from moya.orchestrators.simple_orchestrator import SimpleOrchestrator

class MyAgent:
    def respond(self, message):
        return f"Response to: {message}"

orchestrator = SimpleOrchestrator()
orchestrator.set_agent(MyAgent())
response = orchestrator.orchestrate("thread_id", "Hello, agent!")
print(response)
```

## Custom Orchestrators

You can create custom orchestrators by extending the `Orchestrator` class. This allows you to implement workflows tailored to your specific use case.

#### Example:
```python
from moya.orchestrators.orchestrator import Orchestrator

class CustomOrchestrator(Orchestrator):
    def orchestrate(self, thread_id: str, user_message: str, **kwargs) -> str:
        # Your custom orchestration logic here
        pass

orchestrator = CustomOrchestrator()
orchestrator.add_agent("Agent1")
print(orchestrator.execute_workflow({"task": "example"}))
```

## Additional Notes

- Use `SequentialOrchestrator` for workflows that require strict task order.
- Use `ParallelOrchestrator` for workflows with independent tasks.
- Ensure that orchestrators are thread-safe if used in multi-threaded environments.
- Refer to the individual orchestrator class files for more details on configuration and usage.