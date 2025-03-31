# API Reference

This section provides a detailed reference for all public modules, classes, and methods in Moya.

## Agents

### OpenAIAgent

```python
class OpenAIAgent(Agent):
    """
    A simple OpenAI-based agent that uses the ChatCompletion API.
    """

    def __init__(self, agent_name: str, description: str, agent_config: OpenAIAgentConfig):
        """
        Initialize the OpenAIAgent.

        :param agent_name: Unique name or identifier for the agent.
        :param description: A brief explanation of the agent's capabilities.
        :param agent_config: Configuration for the agent.
        """

    def handle_message(self, message: str) -> str:
        """
        Process a message and return a response.

        :param message: The message to process.
        :return: The agent's response as a string.
        """
```

## Tools

### Tool

```python
class Tool:
    """
    A generic interface for a "tool" that an agent can discover and call.
    """

    def __init__(self, name: str, description: Optional[str], function: Callable):
        """
        Initialize a Tool instance.

        :param name: The name of the tool.
        :param description: A brief description of the tool's functionality.
        :param function: The callable function associated with the tool.
        """
```

## Orchestrators

### SimpleOrchestrator

```python
class SimpleOrchestrator:
    """
    A simple orchestrator that routes all messages to a single default agent.
    """

    def __init__(self, agent_registry: AgentRegistry, default_agent_name: str):
        """
        Initialize the SimpleOrchestrator.

        :param agent_registry: The registry containing available agents.
        :param default_agent_name: The name of the default agent to use.
        """

    def orchestrate(self, thread_id: str, user_message: str) -> str:
        """
        Process a user message and return the agent's response.

        :param thread_id: The identifier of the conversation thread.
        :param user_message: The user's message.
        :return: The agent's response as a string.
        """
```